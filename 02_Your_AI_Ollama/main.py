from langchain.chat_models import init_chat_model
import flask
from flask import Flask, request, jsonify

app = Flask(__name__)


model = init_chat_model(
    model='llama3.2:latest',
    model_provider="ollama"
)


# Flask ловит POST на /chat → вызывается функция chat():
@app.route("/chat", methods=['POST'])
def chat():
    data = request.get_json()

    # отправляется запрос в Ollama (localhost:11434), модель llama3.2:latest генерирует ответ.
    # response — это объект (не просто строка), у него есть .content = "Привет! Как дела?"
    response = model.invoke(data['messages'])

    # Сервер отправляет обратно HTTP-ответ с телом:
    return jsonify(
        {"message": {"role": "assistant",
                     "content": response.content}}
    )



if __name__ == "__main__":
    app.run(debug=True, port=5002)