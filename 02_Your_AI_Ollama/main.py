from langchain.chat_models import init_chat_model
import flask
from flask import Flask, request, jsonify

app = Flask(__name__)


model = init_chat_model(
    model='llama3.2:1b',
    model_provider="ollama"
)

@app.route("/chat", methods=['POST'])
def chat():
    data = request.get_json()
    response = model.invoke(data['messages'])
    return jsonify(
        {"message": {"role": "assistant",
                     "content": response.content}}
    )



if __name__ == "__main__":
    app.run(debug=True, port=5002)