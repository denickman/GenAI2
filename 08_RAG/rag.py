from dotenv import load_dotenv
import os

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.messages import HumanMessage, SystemMessage, AIMessage
from pypdf import PdfReader
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader, TextLoader

'''

Embedding-модель = только "переводчик текст → вектор". Ничего не хранит, ничего не ищет, ничего не сравнивает. 
Просто по запросу говорит "вот тебе вектор для этого текста" и забывает про него.

Vector Store = "картотека" из пар текст+вектор. Именно он выполняет сравнение 
(используя вектора, которые ему когда-то дала embedding-модель) и именно он возвращает результат — 
но возвращает не вектор, а исходный текст, который был прикреплён к самому похожему вектору при индексации.

Так что когда similarity_search возвращает 2 документа — это не embedding-модель их "вернула". 
Это vector_store, используя вектор от embedding-модели как ключ для поиска, нашёл в своей внутренней таблице 
соответствующие оригинальные тексты и отдал их тебе. Embedding-модель — это как GPS-координаты (числа), 
а vector_store — это карта, на которой по этим координатам можно найти реальный адрес (текст) дома.


Files (PDF, TXT)
    │
    ├─→ PyPDFDirectoryLoader  ✅ Удобно
    │
    ▼
Documents (в памяти)
    │
    ├─→ HuggingFaceEmbeddings (LOCAL) ✅ Локально, бесплатно
    ├─→ GoogleGenerativeAIEmbeddings (REMOTE) ✅ На Google серверах, лучше качество
    │
    ▼
Vector Store (InMemory) ✅ В памяти
    │
    ├─→ Similarity Search
    │
    ▼
TOP-2 Documents ✅ Только релевантные
    │
    ├─→ Context (Small String)
    │
    ▼
System Prompt + Context + User Query
    │
    ├─→ LLM (Google Gemini)
    │
    ▼
Response ✅ Окончательный ответ
'''

'''
ВАРИАНТЫ EMBEDDINGS:

1️⃣ LOCAL (HuggingFace):
   https://huggingface.co/models

   from langchain_huggingface import HuggingFaceEmbeddings

   # МАЛЕНЬКИЕ (быстрые, на слабых компьютерах)
   embeddings = HuggingFaceEmbeddings(model='sentence-transformers/all-MiniLM-L6-v2')
   # ✅ Размер: 90MB
   # ✅ Скорость: быстро
   # ✅ Качество: хорошо
   # ✅ Память: 500MB

   # СРЕДНИЕ (оптимальные)
   embeddings = HuggingFaceEmbeddings(model='sentence-transformers/all-mpnet-base-v2')
   # ✅ Размер: 430MB
   # ✅ Скорость: средняя
   # ✅ Качество: отличное
   # ✅ Память: 2GB

   # БОЛЬШИЕ (лучший результат, но медленно)
   embeddings = HuggingFaceEmbeddings(model='sentence-transformers/all-roberta-large-v1')
   # ✅ Размер: 500MB
   # ✅ Скорость: медленно
   # ✅ Качество: лучшее
   # ✅ Память: 3GB

2️⃣ REMOTE (Google):
   https://ai.google.dev/docs/models

   from langchain_google_genai import GoogleGenerativeAIEmbeddings

   # Модели Google
   embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
   # ✅ Размер: на Google серверах
   # ✅ Скорость: зависит от интернета
   # ✅ Качество: лучшее
   # ✅ Стоимость: $0.075 за 1M токенов
   # ✅ Приватность: Google видит текст
'''

# https://ai.google.dev/docs/models
# https://huggingface.co/models

load_dotenv()

directory = "My Documents"


# ═════════════════════════════════════════════════
# ФУНКЦИЯ: LOCAL EMBEDDINGS
# ═════════════════════════════════════════════════

def run_rag_local():
    """RAG с локальными embeddings (бесплатно, приватно)"""

    print("\n" + "=" * 60)
    print("🏠 LOCAL RAG - HuggingFace Embeddings")
    print("=" * 60 + "\n")

    # set up llm
    llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

    # load documents
    print("📚 Загружаем документы...")
    pdf_loader = PyPDFDirectoryLoader(directory)
    pdf_docs = pdf_loader.load()

    text_loader = DirectoryLoader(directory, glob='**/*.txt', loader_cls=TextLoader)
    text_docs = text_loader.load()

    # csv_loader = DirectoryLoader(directory, glob='**/*.csv', loader_cls=TextLoader)
    # csv_docs = csv_loader.load()

    docs = pdf_docs + text_docs
    print(f"✅ Загружено документов: {len(docs)}\n")

    # 2. Embeddings локально
    # При первом запуске: загружает модель (~100MB)
    # Следующие запуски: использует из памяти
    """
    Embeddings — превращение текста в числа
    создаётся модель, которая умеет превращать любой текст в вектор — список чисел фиксированной длины 
    (например, 384 числа). 
    """
    print("🤖 Создаём локальные embeddings (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(model='sentence-transformers/all-MiniLM-L6-v2')
    print("✅ Embeddings готовы (живут на ТВОЁМ компьютере)\n")

    # 3. Vector Store в памяти
    print("💾 Создаём Vector Store в памяти...")
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(docs)
    print("✅ Vector Store готов\n")

    # Диалог с пользователем
    print("💬 Чат начат (введи 'exit' для выхода)\n")

    while True:
        user_query = input("📝 Your question: ")

        if user_query.lower() == 'exit':
            print("👋 До свидания!")
            break

        # Retrieved TOP-2 релевантных документов
        retrieved_docs = vector_store.similarity_search(user_query, k=2)

        # Создание контекста из TOP-2
        context = '\n'.join(doc.page_content for doc in retrieved_docs)

        # System Prompt с контекстом
        system_prompt = f"""You are a helpful assistant about these documents:{context}"""

        # Подготовка сообщений
        messages = [SystemMessage(content=system_prompt)]
        messages.append(HumanMessage(content=user_query))

        # Отправка в LLM
        response = llm.invoke(messages)

        print(f"\n🤖 Assistant: {response.content}\n")


# ═════════════════════════════════════════════════
# ФУНКЦИЯ: REMOTE EMBEDDINGS
# ═════════════════════════════════════════════════

def run_rag_remote():
    """RAG с удалёнными embeddings (Google, лучше качество)"""

    print("\n" + "=" * 60)
    print("☁️  REMOTE RAG - Google Embeddings")
    print("=" * 60 + "\n")

    # set up llm
    llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

    # load documents
    print("📚 Загружаем документы...")
    pdf_loader = PyPDFDirectoryLoader(directory)
    pdf_docs = pdf_loader.load()

    text_loader = DirectoryLoader(directory, glob='**/*.txt', loader_cls=TextLoader)
    text_docs = text_loader.load()

    # csv_loader = DirectoryLoader(directory, glob='**/*.csv', loader_cls=TextLoader)
    # csv_docs = csv_loader.load()

    docs = pdf_docs + text_docs
    print(f"✅ Загружено документов: {len(docs)}\n")

    # 2. Embeddings удалённо (Google)
    # Отправляет текст на Google серверы
    # Получает вектор обратно
    print("🌐 Создаём удалённые embeddings (Google)...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    print("✅ Embeddings готовы (работают на Google серверах)\n")

    # 3. Vector Store в памяти
    print("💾 Создаём Vector Store в памяти...")
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(docs)
    print("✅ Vector Store готов\n")

    # Диалог с пользователем
    print("💬 Чат начат (введи 'exit' для выхода)\n")

    while True:
        user_query = input("📝 Your question: ")

        if user_query.lower() == 'exit':
            print("👋 До свидания!")
            break

        # Retrieved TOP-2 релевантных документов
        retrieved_docs = vector_store.similarity_search(user_query, k=2)

        # Создание контекста из TOP-2
        context = '\n'.join(doc.page_content for doc in retrieved_docs)

        # System Prompt с контекстом
        system_prompt = f"""You are a helpful assistant about these documents: {context}"""

        # Подготовка сообщений
        messages = [SystemMessage(content=system_prompt)]
        messages.append(HumanMessage(content=user_query))

        # Отправка в LLM
        response = llm.invoke(messages)

        print(f"\n🤖 Assistant: {response.content}\n")


# ═════════════════════════════════════════════════
# МЕНЮ: ВЫБОР ВАРИАНТА
# ═════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🤖 RAG CHATBOT - Выбери тип embeddings")
    print("=" * 60)

    print("\n1️⃣  LOCAL EMBEDDINGS (HuggingFace)")
    print("   ✅ Бесплатно")
    print("   ✅ Приватно (100%)")
    print("   ✅ Без интернета")
    print("   ✅ Быстро (после загрузки модели)")
    print("   ❌ Качество: хорошее (но не лучшее)")
    print("   Модель: sentence-transformers/all-MiniLM-L6-v2 (90MB)")

    print("\n2️⃣  REMOTE EMBEDDINGS (Google)")
    print("   ✅ Лучше качество")
    print("   ✅ Профессиональное решение")
    print("   ❌ Платно ($0.075 за 1M токенов)")
    print("   ❌ Google видит текст")
    print("   ❌ Нужен интернет")
    print("   Модель: text-embedding-004")

    choice = input("\n👉 Выбери (1 или 2): ").strip()

    if choice == "1":
        run_rag_local()
    elif choice == "2":
        run_rag_remote()
    else:
        print("\n❌ Неверный выбор! Пожалуйста, введи 1 или 2")