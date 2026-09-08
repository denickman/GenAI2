from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage, SystemMessage, AIMessage
from pypdf import PdfReader
from pathlib import Path

load_dotenv()

documents = []


def load_docs(directory='My Documents'):
    for file_path in Path(directory).rglob('*'):
        if file_path.suffix in {'.txt', '.pdf', '.md'}:
            if file_path.suffix == '.pdf':
                reader = PdfReader(file_path)
                content = '\n'.join(page.extract_text() for page in reader.pages)
            else:
                content = file_path.read_text()

            documents.append({
                'path': str(file_path.relative_to(directory)),
                'content': content,
            })
    return documents


def create_context(document_list):
    context = ''
    for doc in document_list:
        context += f'______{doc["path"]}______\n{doc["content"]}\n\n'
    return context


documents = load_docs()
context = create_context(documents)

llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

system_prompt = f"""
You are a helpful assistant about these documents:
{context}
"""



"""
SystemMessage(content=...) — роль system. Это инструкция "как себя вести", задаётся один раз в начале, 
модель воспринимает её как правила игры, а не как реплику пользователя.
HumanMessage(content=...) — роль user. То, что написал человек.
AIMessage(content=...) — роль assistant. То, что ответила модель. Её добавляют в историю после ответа модели, 
чтобы при следующем запросе модель "помнила", что сама уже сказала.
"""

# ✅ ОПТИМИЗАЦИЯ: Ограничиваем историю
MAX_HISTORY = 10  # Храним только 10 последних сообщений

messages = [SystemMessage(content=system_prompt)]

print("🤖 RAG Chat (с оптимизацией)")
print(f"📝 Max history: {MAX_HISTORY}")
print("-" * 50)

while True:
    user_query = input("\n📝 Your question: ")

    if user_query.lower() == 'exit':
        break

    messages.append(HumanMessage(content=user_query))

    # ✅ ОПТИМИЗАЦИЯ: Если история слишком длинная - удаляем старые сообщения
    if len(messages) > MAX_HISTORY:
        # Удаляем старое сообщение (не трогаем SystemMessage в начале)
        messages.pop(1)
        print(f"⚠️ History trimmed to {MAX_HISTORY} messages")

    print(f"📊 Total messages in history: {len(messages)}")

    try:
        response = llm.invoke(messages)
        messages.append(AIMessage(content=response.content))
        print(f"\n🤖 Assistant: {response.content}")
    except Exception as e:
        print(f"❌ Error: {e}")
        messages.pop()