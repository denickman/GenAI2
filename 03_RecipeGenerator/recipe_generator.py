from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List

"""
Этот скрипт решает другую задачу: не просто получить текст от модели, 
а получить ответ в строго заданной структуре (как настоящий объект Python, 
а не текст, который потом нужно парсить вручную).

Pydantic — библиотека, которая позволяет описать схему данных — как должен выглядеть объект, 
какие у него поля и какого они типа. Это как чертёж:

Field(description=...) — это не просто комментарий для тебя, это 
инструкция для модели — она передаётся модели как подсказка, что именно должно быть в этом поле.
"""

load_dotenv()

class Recipe(BaseModel):
    name: str = Field(description="Name of the recipe")
    description: str = Field(description = "Brief description of the recipe")
    prep_time: str = Field(description="Estimated preparation time of the recipe")

class Response(BaseModel):
    """A single recipe"""
    ingredients: List[str] = Field(description="List of main ingredients")
    recipes: List[Recipe] = Field(description="List of 3 recipe suggestions")



# Initialize the model
# "Заставляем" модель отвечать строго в этой структуре
"""
.with_structured_output(Response) — оборачивает обычную модель так,
 что она не может ответить вольным текстом — LangChain под капотом заставляет модель вернуть данные, 
 которые точно соответствуют схеме Response (обычно через tool calling или JSON mode — в зависимости от провайдера).
"""
model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
structured_model = model.with_structured_output(Response)
system_prompt = """
"You are a helpful chef. Identify the main ingredients. Suggest 3 recipes based those ingredients."
"""

# Create message
message = [{"role": "system", "content": system_prompt},
           {"role": "user", "content": "I have broccoli, butter, and eggs."}]

# Get and print the response
response = structured_model.invoke(message)
print(response.model_dump())
# .model_dump() — метод Pydantic, который превращает объект обратно в обычный Python-словарь (dict),
# удобный для вывода/сериализации в JSON.