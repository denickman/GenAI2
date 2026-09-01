import requests

API_URL = "http://localhost:5002"

url = f"{API_URL}/chat"

history = []

while True:
    user_input = input("You: ")
    history.append({"role": "user", "content": user_input})

    # Отправляется реальный HTTP-запрос на сервер (терминал 1 - main.app). Тело запроса (JSON):
    # и потом
    #  requests.post(...) наконец получает ответ (строка response = requests.post(...) наконец "разблокировалась") —
    #  response теперь содержит этот JSON.
    response = requests.post(
        url,
        json={"messages": history})

    assistant_message = response.json()['message']
    history.append(assistant_message)
    print(assistant_message['content'])