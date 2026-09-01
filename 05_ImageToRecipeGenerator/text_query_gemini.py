"""
Simple Text Chat using LangChain v1 and Google Gemini
pip install langchain langchain-google-genai python-dotenv
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

# Initialize the model
model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

# Create message
message = {"role": "user", "content": "What is the capital of France?"}

# Get and print the response
response = model.invoke([message])
print(response.text)