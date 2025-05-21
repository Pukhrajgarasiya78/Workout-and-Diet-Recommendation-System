import google.generativeai as genai
from flask import current_app

def init_gemini():
    api_key = current_app.config['GEMINI_API_KEY']
    if not api_key:
        raise ValueError("Gemini API key not found in configuration")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash') 