import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model

load_dotenv()

GOOGLE_SPREADSHEET_API_KEY = os.getenv("GOOGLE_SPREADSHEET_API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # было GEMINI_API_KEY
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
LAST_ROW_FILE = "last_row.txt"


def get_last_row():
    """Читает индекс последней обработанной строки.
    Если файла нет (первый запуск) — считаем, что обработано 0 строк."""
    if not os.path.exists(LAST_ROW_FILE):
        return 0
    with open(LAST_ROW_FILE) as file:
        content = file.read().strip()
        return int(content) if content else 0


def save_last_row(value):
    with open(LAST_ROW_FILE, "w") as file:
        file.write(str(value))


def fetch_with_retry(service, max_attempts=4, base_delay=2):
    """Повторяет запрос при временных ошибках Google (503, 500, 429)."""
    for attempt in range(1, max_attempts + 1):
        try:
            return service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME
            ).execute()
        except HttpError as e:
            status = e.resp.status if hasattr(e, "resp") else None
            if status in (500, 503, 429) and attempt < max_attempts:
                delay = base_delay * attempt
                print(f"Google API вернул {status}, повтор через {delay}с "
                      f"(попытка {attempt}/{max_attempts})...", file=sys.stderr)
                time.sleep(delay)
                continue
            raise


def get_spreadsheet_data():
    """Fetch spreadsheet data"""
    service = build('sheets', 'v4', developerKey=GOOGLE_SPREADSHEET_API_KEY)
    result = fetch_with_retry(service)
    all_rows = result.get('values', [])
    if not all_rows:
        return [], [], []

    last_row = get_last_row()
    headers = all_rows[0]
    # не даём new_rows начинаться раньше конца заголовков
    start = max(last_row, 1)
    new_rows = all_rows[start:]
    return all_rows, new_rows, headers


def summarize_with_ai(text):
    system_prompt = (
        "You are a helpful assistant that summarizes spreadsheet data. "
        "You will receive new rows that were added to a Google Spreadsheet. "
        "Please provide a clear, concise summary of this data."
    )
    model = init_chat_model(
        "claude-sonnet-4-6",
        api_key=ANTHROPIC_API_KEY,
        model_provider="anthropic",
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here are the new rows from the spreadsheet \n {text}"},
    ]
    response = model.invoke(messages).content
    return response


def send_email(subject, body):
    """Send email with the summary."""
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    try:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
    finally:
        server.quit()
    print(f"Email sent successfully to {RECIPIENT_EMAIL}")


def main():
    try:
        all_rows, new_rows, headers = get_spreadsheet_data()
    except Exception as e:
        print(f"Ошибка при чтении таблицы: {e}", file=sys.stderr)
        sys.exit(1)

    if not new_rows:
        print("Новых строк нет — выходим без отправки письма.")
        return

    message = f"Headers: {headers} \nNew rows: {new_rows}"

    try:
        summary = summarize_with_ai(message)
    except Exception as e:
        print(f"Ошибка при обращении к AI-модели: {e}", file=sys.stderr)
        # last_row.txt пока НЕ трогаем — новые строки не потеряны,
        # при следующем запуске скрипт попробует обработать их снова
        sys.exit(1)

    body = f"Here is today's summary \n\n{summary}\n\n Thanks!"

    try:
        send_email("Daily Spreadsheet Summary", body)
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}", file=sys.stderr)
        # тоже не обновляем last_row.txt — письмо не ушло,
        # значит прогресс не засчитан
        sys.exit(1)

    # last_row.txt обновляем ТОЛЬКО после успешной отправки письма
    save_last_row(len(all_rows))
    print("Готово. last_row.txt обновлён.")


if __name__ == "__main__":
    main()