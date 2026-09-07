import os
import tempfile
import sounddevice as sd # запись и воспроизведение аудио через микрофон/динамики.
import soundfile as sf # чтение/запись аудиофайлов (WAV, MP3 и т.д.).
import openai
from dotenv import load_dotenv

'''
┌──────────────────────────────────────────────────────┐
│ 1️⃣  ТЫ ГОВОРИШЬ В МИКРОФОН                          │
│    (Звуковая волна)                                  │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ 2️⃣  ЗАПИСЬ В WAV ФАЙЛ                                │
│    (record_audio)                                    │
│    Сохраняется как /tmp/xyz.wav                      │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ 3️⃣  ОТПРАВКА НА WHISPER API (OpenAI)               │
│    (transcribe)                                      │
│    Преобразование аудио → текст                      │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ "You said: Hello, how are you?"                      │
│ (Выводится в консоль)                               │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ 4️⃣  ОТПРАВКА НА GPT API (OpenAI)                    │
│    (think)                                           │
│    Обработка текста и генерация ответа              │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ "AI: I'm doing great, thank you for asking!"        │
│ (Выводится в консоль)                               │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ 5️⃣  ОТПРАВКА НА TTS API (OpenAI)                    │
│    (speak)                                           │
│    Преобразование текста → аудио                     │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ 6️⃣  ВОСПРОИЗВЕДЕНИЕ ЧЕРЕЗ ДИНАМИКИ                  │
│    (sd.play)                                         │
│    Ты слышишь голос ИИ!                             │
└──────────────────────────────────────────────────────┘
'''

load_dotenv()

client = openai.OpenAI()

SAMPLE_RATE = 16000 # частота дискретизации записи (16 кГц, стандартно для распознавания речи).
MAX_DURATION = 30


def record_audio() -> str:
    """Record from microphone, return path to temp WAV file."""

    # ШАГ 1: Ждём пока ты нажмёшь Enter
    input("Press Enter to start recording...")
    print("Recording... Press Enter to stop.")

    # ШАГ 2: Записываем аудио с микрофона
    """
    sd.rec() — асинхронный, он не блокирует поток, поэтому запись идёт параллельно, пока скрипт "спит" на input(). 
    Как только пользователь жмёт Enter — input() возвращает управление, и вызывается sd.stop().
    """
    audio_data = sd.rec(
        int(MAX_DURATION * SAMPLE_RATE),  # 30сек * 16000 = 480000 семплов
        samplerate=SAMPLE_RATE,  # 16000 Hz (качество записи)
        channels=1,  # Моно (1 канал, не стерео)
        dtype="float64",  # Формат данных
    )

    # ШАГ 3: Ждём пока ты нажмёшь Enter чтобы остановить
    input()
    sd.stop()  # Останавливаем запись
    print("Recording stopped.")

    # ШАГ 4: Сохраняем в WAV файл
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp.name, audio_data, SAMPLE_RATE)

    # ШАГ 5: Возвращаем путь к файлу
    return tmp.name


def transcribe(audio_path: str) -> str:
    # ШАГ 1: Открой WAV файл
    """Send audio to OpenAI Whisper API and return the transcript."""
    with open(audio_path, "rb") as f:
        # ШАГ 2: Отправь на Whisper API
        return client.audio.transcriptions.create(
            model="whisper-1",  # Модель распознавания речи
            file=f,  # Твой WAV файл
            response_format="text",  # Вернуть просто текст
        )


# ШАГ 1: Отправь текст на GPT
def think(text: str) -> str:
    """Send text to GPT and return the response."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Модель ИИ
        messages=[
            # Системный промпт (характер ассистента)
            {"role": "system",
             "content": "You are a helpful voice assistant. Keep responses short and conversational."},
            # Твой вопрос
            {"role": "user", "content": text},
        ],
    )
    # ШАГ 2: Извлеки ответ
    return response.choices[0].message.content


def speak(text: str):
    """Convert text to speech and play it."""

    # ШАГ 1: Создай временный MP3 файл
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)

    # ШАГ 2: Отправь текст на TTS API (Text-To-Speech)
    with client.audio.speech.with_streaming_response.create(
            model="tts-1",  # Модель синтеза речи
            voice="nova",  # Голос женщины
            input=text,  # "I'm doing great..."
    ) as response:
        # Сохрани в MP3
        response.stream_to_file(tmp.name)

    # ШАГ 3: Прочитай MP3 файл
    data, sr = sf.read(tmp.name)

    # ШАГ 4: Проиграй через динамики
    sd.play(data, sr)

    # Жди пока закончится воспроизведение
    sd.wait()

    # ШАГ 5: Удали временный файл
    os.unlink(tmp.name)


audio_file = record_audio()

transcript = transcribe(audio_file)
print(f"\nYou said: {transcript}")
os.unlink(audio_file)

reply = think(transcript)
print(f"AI: {reply}")

speak(reply)

'''
# ГЛАВНЫЙ КОД:
audio_file = record_audio()
# ↓ Вывод:
# Press Enter to start recording...
# (ты говоришь)
# Recording stopped.
# ↓ Возвращает: "/tmp/xyz.wav"


transcript = transcribe(audio_file)
# ↓ Отправляет /tmp/xyz.wav на Whisper
# ↓ Получает: "Hello, how are you?"
print(f"\nYou said: {transcript}")
# Вывод: "You said: Hello, how are you?"

os.unlink(audio_file)
# ↓ Удаляет "/tmp/xyz.wav" (больше не нужен)


reply = think(transcript)
# ↓ Отправляет "Hello, how are you?" на GPT
# ↓ Получает: "I'm doing great, thank you for asking!"
print(f"AI: {reply}")
# Вывод: "AI: I'm doing great, thank you for asking!"


speak(reply)
# ↓ Отправляет текст на TTS
# ↓ Преобразует в MP3
# ↓ Воспроизводит звук
# ↓ ТЫ СЛЫШИШЬ ОТВЕТ!

'''

'''
═══════════════════════════════════════════════════════════

🎤 ЭТАП 1: ЗАПИСЬ
Press Enter to start recording...
[ТЫ НАЖИМАЕШЬ ENTER]
Recording... Press Enter to stop.
[ТЫ ГОВОРИШЬ: "What is the capital of France?"]
[НАЖИМАЕШЬ ENTER]
Recording stopped.

═══════════════════════════════════════════════════════════

📝 ЭТАП 2: ТРАНСКРИБАЦИЯ (Whisper)
[ОТПРАВЛЯЕТСЯ НА OpenAI]
[Whisper анализирует твой голос]
Получен результат: "What is the capital of France?"

You said: What is the capital of France?

═══════════════════════════════════════════════════════════

🧠 ЭТАП 3: ОБРАБОТКА (GPT)
[ОТПРАВЛЯЕТСЯ НА OpenAI]
[GPT думает и генерирует ответ]
Получен результат: "The capital of France is Paris."

AI: The capital of France is Paris.

═══════════════════════════════════════════════════════════

🔊 ЭТАП 4: СИНТЕЗ РЕЧИ (TTS)
[ОТПРАВЛЯЕТСЯ НА OpenAI]
[TTS синтезирует голос]
[Воспроизводится через динамики]

[ТЫ СЛЫШИШЬ ГОЛОС: 
 "The capital of France is Paris."]

═══════════════════════════════════════════════════════════


файлы которые создаются 
1. /tmp/tmpABC123.wav
   ├─ Создаётся при записи
   └─ Удаляется после транскрибации

2. /tmp/tmpDEF456.mp3
   ├─ Создаётся при TTS
   ├─ Воспроизводится
   └─ Удаляется в конце speak()




АПИ Вызовы 

Твой код → OpenAI API → Результат

Вызов 1:
  local: record_audio() → /tmp/xyz.wav
  ↓
Вызов 2:
  CLOUD: Whisper("Здравствуй") → "Здравствуй"
  ↓
Вызов 3:
  CLOUD: GPT("Здравствуй") → "Привет! Как дела?"
  ↓
Вызов 4:
  CLOUD: TTS("Привет!...") → audio.mp3
  ↓
local: play(audio.mp3) → ЗВУК!



Итоговая система 

ВХОД (твой голос) 
    ↓
record_audio()      [Локальное] → WAV файл
    ↓
transcribe()        [API] → Текст твоей речи
    ↓
think()             [API] → Ответ ИИ (текст)
    ↓
speak()             [API] → Синтез + [Локальное] → Воспроизведение
    ↓
ВЫХОД (голос ИИ в динамиках)

+ КОНСОЛЬ:
  You said: [твой текст]
  AI: [ответ ИИ]

'''