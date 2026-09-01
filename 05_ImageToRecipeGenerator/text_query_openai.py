"""
Simple Text Chat using LangChain v1 and OpenAI
pip install langchain langchain-openai python-dotenv
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

# Initialize the model
model = init_chat_model("gpt-4.1-nano", model_provider="openai")

# Create message
message = {"role": "user", "content": "What is the capital of Tokyo? Answer in 3 words."}

# Get and print the response
response = model.invoke([message])
print(response.text)