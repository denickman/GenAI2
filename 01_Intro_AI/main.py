

# weather api
# https://openweathermap.org/
# go to username -> my api keys -> ff00bc12afdeefb603f6c4040f8cecc0



# pip install langchain
# pip install langchain-google-genai


# go to aistudio.google.com
# on the left side panel - select "get API key" -> Create API Key button
# name your API Key then choose or create a project


from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()



def get_weather(city: str):
    """
    Use this when user asks about the weather
    """
    # request.get()
    return {'condition':'sunny', 'temperature': 25}


def get_location():
    """
        Get user`s location, use this when the user asks about the weather without specifiyng the city
        Use this when user asks about the location
    """
    return 'Rome, Italy'



# init gemini flash 2.5
llm = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',
    temperature=0.7,
)

#response1 = llm.invoke("how is the weather in rome?")
#print(response1)


system_prompt = """
    You are a helpful weather assistant.

    Your workflow:
    
    first - call get_location()
    second - call get_weather()
    
    if the user provides a city, call the get_weather() directly without calling get location. 

    Always base your answer on tool output, not on prior knowledge — weather changes constantly.
"""

agent = create_agent(
    model=llm,
    tools=[get_weather, get_location],
    system_prompt=system_prompt
)


user_query = input("Enter your query: ")







response1 = agent.invoke({
    "messages": [{
        "role":"user",
        "content": user_query
    }]
})

print(response1.content)
print(response1['messages'][-1]['content'])
















'''

# see gogle gemini models to choose appropriate one

Ключи gemini google keys
https://aistudio.google.com/app/api-keys


model = init_chat_model(model="gemini-3-flash-preview", model_provider="google-genai", api_key=GOOGLE_API_KEY)


with open('wood.txt') as f:
    wood = f.read()


response = model.invoke(f"from which material this furniture is {wood}")
print(response.content[0]['text'])


'''