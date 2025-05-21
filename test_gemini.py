import os
import google.generativeai as genai
from dotenv import load_dotenv
from app import create_app
from app.utils.ai_helper import test_gemini_connection, generate_diet_plan, generate_workout_plan
from flask import current_app

def test_gemini_connection():
    try:
        # Load environment variables
        load_dotenv()
        
        # Configure API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Initialize model with configuration
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Test the connection
        chat = model.start_chat()
        response = chat.send_message("Hello, this is a test message.")
        print("Response:", response.text)
        
        return True
    except Exception as e:
        print(f"Error testing Gemini connection: {str(e)}")
        return False

# Create the Flask application instance
app = create_app()

def test_connection():
    with app.app_context():
        # Test Gemini connection
        success = test_gemini_connection()
        print(f"\nGemini Connection Test:")
        print(f"Success: {success}")

        if success:
            # Test diet plan generation
            class MockUser:
                def __init__(self):
                    self.age = 30
                    self.gender = 'male'
                    self.weight = 70
                    self.height = 170
                    self.activity_level = 'moderate'
                    self.fitness_goal = 'maintain_weight'
                    self.dietary_preference = 'non-vegetarian'
                    self.health_conditions = None
                    self.dietary_restrictions = None

            user = MockUser()
            print("\nTesting Diet Plan Generation:")
            diet_plan = generate_diet_plan(user)
            if diet_plan:
                print("Diet plan generated successfully!")
                print(f"Daily Calories: {diet_plan.get('daily_calories')}")
                print(f"Number of meals: {len(diet_plan.get('meals', []))}")
            else:
                print("Failed to generate diet plan")

            print("\nTesting Workout Plan Generation:")
            workout_plan = generate_workout_plan(user)
            if workout_plan:
                print("Workout plan generated successfully!")
                print(f"Workout type: {workout_plan.get('workout_type')}")
                print(f"Duration: {workout_plan.get('duration')} minutes")
            else:
                print("Failed to generate workout plan")

if __name__ == '__main__':
    test_connection() 