from google import genai
from dotenv import load_dotenv
import os

'''
┌─────────────────────────────────────────┐
│ 1️⃣  load_dotenv()                      │
│    Читаю .env файл                      │
│    GOOGLE_API_KEY загружена             │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 2️⃣  genai.Client(api_key=...)           │
│    Создаю клиент для API                │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 3️⃣  generate_content(...)               │
│    Отправляю запрос в Google            │
│    "Создай изображение птицы"           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 4️⃣  Google генерирует изображение       │
│    Возвращает response с данными        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 5️⃣  if response.parts:                  │
│    Проверяю что получил ответ           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 6️⃣  part = response.parts[0]            │
│    Беру первую часть ответа             │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 7️⃣  if hasattr(part, 'inline_data'):    │
│    Проверяю что это изображение         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 8️⃣  image_bytes = part.inline_data.data │
│    Извлекаю бинарные данные            │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 9️⃣  with open('...', 'wb') as f:       │
│    f.write(image_bytes)                 │
│    Сохраняю на диск                     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ ✅ generated_image.png создан!          │
│    Изображение на диске готово!         │
└──────────────────────────────────────────┘
'''

load_dotenv()
key = os.getenv("GOOGLE_API_KEY")
print(f"Ключ: {repr(key)}")  # временно, чтобы увидеть, что реально загрузилось




client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input="Explain how AI works in a few words"
)
print("====INTERACTION====")
print(interaction.output_text)




response = client.models.generate_content(
    model='gemini-3-pro-image-preview',
    contents=['create me an image of a bird swimming in the sea']
)

# Проверка и сохранение
try:
    if response.parts and len(response.parts) > 0:
        part = response.parts[0]

        if hasattr(part, 'inline_data'):
            image_bytes = part.inline_data.data

            with open('generated_image.png', 'wb') as f:
                f.write(image_bytes)

            print("✅ Image saved as generated_image.png")
except Exception as e:
    print(f"❌ Error: {e}")