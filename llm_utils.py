import google.generativeai as genai
from google.generativeai import list_models
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")

def ask_gemini(context, query):
    prompt = f"Given the context:\n{context}\nAnswer the question:\n{query}"
    response = model.generate_content(prompt)
    return response.text


# models = list_models()
# for model in models:
#     print(model.name)
