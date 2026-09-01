import gradio as gr
import base64
import mimetypes
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

system_prompt = """
You are a helpful chef. Identify the main ingredients. Suggest 3 recipes based on those ingredients.
"""

def identify_ingredients(image_path):
    if image_path is None:
        return "Пожалуйста, загрузите изображение."

    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "image/jpeg"

    with open(image_path, 'rb') as file:
        image_base64 = base64.b64encode(file.read()).decode("utf-8")

    message = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source_type": "base64",
                    "data": image_base64,
                    "mime_type": mime_type,
                }
            ],
        },
    ]

    response = model.invoke(message)
    return response.content

demo = gr.Interface(
    fn=identify_ingredients,
    inputs=gr.Image(type="filepath"),
    outputs=gr.Markdown(),
    title='Recipe Generator',
    description="Upload an image with ingredients",
    flagging_mode="never",
)

demo.launch(debug=True)