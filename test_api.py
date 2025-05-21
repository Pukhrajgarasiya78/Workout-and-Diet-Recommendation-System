import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_api():
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    try:
        response = model.generate_content("Hello, how are you?")
        print("Response:", response.text)
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    test_api() 