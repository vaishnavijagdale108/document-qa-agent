from google import genai
from dotenv import load_dotenv
load_dotenv()
import os


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_answer(question, context):
    prompt = f"""
    Answer the question using only the provided context.

    Context:
    {context}

    Question:
    {question}
    """
    response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
    )

    return response.text