"""
Simple Text Chat using LangChain v1 and Anthropic Claude
pip install langchain langchain-anthropic python-dotenv
"""
import base64
import mimetypes

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()


image_path='images/img.png'
mime_type = mimetypes.MimeTypes().guess_type(image_path)[0]

with open(image_path, "rb") as image_file:
    raw_binary_data = image_file.read()
    image_bytes = base64.b64encode(raw_binary_data) # raw bytes of image
    image_base64 = image_bytes.decode("utf-8")
    print(image_base64)


# Initialize the model
model = init_chat_model("claude-sonnet-4-6", model_provider="anthropic")

# Create message
# message = [{"role": "user", "content": "What is the capital of France?"}]


message = [{
    "role": "user",
            "content": [
                        {"type": "text", "text": "Describe what you see in this image?"},
                        {"type": "image", "base64": image_base64, "mime_type": mime_type},
                        ]



            }]


# Get and print the response
response = model.invoke(message)
print("====RESPONSE====")
print(response)