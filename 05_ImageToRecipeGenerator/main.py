"""
Simple Text Chat using LangChain v1 and Anthropic Claude
pip install langchain langchain-anthropic python-dotenv
"""
import base64
import mimetypes

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()


image_path = 'images/ingredients.png'
mime_type, _ = mimetypes.guess_type(image_path)

if mime_type is None:
    raise ValueError(f"Не удалось определить mime_type для файла: {image_path}")

with open(image_path, "rb") as image_file:
    raw_binary_data = image_file.read()
    image_base64 = base64.b64encode(raw_binary_data).decode("utf-8")

# Initialize the model
model = init_chat_model("claude-sonnet-4-6", model_provider="anthropic")

system_prompt = """
You are a helpful chef. identify the main ingredients. suggest 3 recipes
"""


# Create message
message = [

    {
        "role":"system", "content":system_prompt,
    },



    {
    "role": "user",
    "content": [
        {
            "type": "image",
            "source_type": "base64",
            "data": image_base64,
            "mime_type": mime_type,
        },
    ],
}
]

# Get and print the response
response = model.invoke(message)
print(response.content)