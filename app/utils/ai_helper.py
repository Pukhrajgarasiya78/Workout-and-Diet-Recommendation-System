import os
import time
import json
import google.generativeai as genai
from google.api_core import retry
from flask import current_app
from app.config import Config
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

def test_gemini_connection():
    """Test the Gemini API connection and model availability"""
    try:
        model = init_gemini()
        if not model:
            return False, "Failed to initialize Gemini model"
            
        # Test with a simple prompt
        test_prompt = "Hi, this is a test message. Please respond with 'OK' if you receive this."
        response = model.generate_content(test_prompt)
        
        if response and response.text:
            return True, "Gemini API connection successful"
        else:
            return False, "No response received from Gemini API"
            
    except Exception as e:
        return False, f"Error testing Gemini API: {str(e)}"

def init_gemini():
    """Initialize the Gemini model with API key"""
    try:
        # Configure the API key
        api_key = current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in configuration")
        
        genai.configure(api_key=api_key)
        
        # Create model instance with configuration
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
        response = model.generate_content("Test connection")
        if not response.text:
            raise Exception("Failed to get response from Gemini model")
        
        return model
    except Exception as e:
        current_app.logger.error(f"Error initializing Gemini model: {str(e)}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_diet_plan(user):
    """Generate a personalized diet plan using Gemini AI"""
    try:
        model = init_gemini()
        if not model:
            current_app.logger.error("Failed to initialize Gemini model")
            return get_fallback_diet_plan()
        
        # Calculate BMR and calorie needs
        bmr = calculate_bmr(user)
        daily_calories = calculate_daily_calories(bmr, user)
        protein_target = calculate_protein_target(user, daily_calories)
        
        # Build user profile section
        user_profile = f"""
        User Profile:
        - Age: {getattr(user, 'age', 'Not specified')}
        - Gender: {getattr(user, 'gender', 'Not specified')}
        - Weight: {getattr(user, 'weight', 'Not specified')} kg
        - Height: {getattr(user, 'height', 'Not specified')} cm
        - Activity Level: {getattr(user, 'activity_level', 'moderate')}
        - Fitness Goal: {getattr(user, 'fitness_goal', 'maintain_weight')}
        - Dietary Preference: {getattr(user, 'dietary_preference', 'non-vegetarian')}
        - Health Conditions: {getattr(user, 'health_conditions', 'None')}
        - Dietary Restrictions: {getattr(user, 'dietary_restrictions', 'None')}"""

        # Build targets section
        targets = f"""
        Required Targets:
        - Daily Calorie Target: {daily_calories} calories
        - Protein Target: {protein_target}g"""

        # Define requirements section
        requirements = """
        Requirements:
        1. Create a COMPLETELY NEW and UNIQUE meal plan - DO NOT use templates
        2. Ensure meals are culturally appropriate and seasonally relevant
        3. Consider the user's dietary restrictions and health conditions
        4. Include specific portion sizes and preparation methods
        5. Provide detailed macronutrient breakdowns
        6. Suggest timing for each meal based on activity level
        7. Include at least 2 alternative options for each meal
        8. Add specific notes about food allergies and interactions
        9. Include micronutrient considerations
        10. Provide tips for meal prep and storage"""

        # Define JSON format
        json_format = """
        {
            "daily_calories": int,
            "daily_protein": int,
            "meals": [
                {
                    "meal_type": string,
                    "suggested_time": string,
                    "foods": [
                        {
                            "name": string,
                            "preparation": string,
                            "portion": string,
                            "calories": int,
                            "protein": float,
                            "carbs": float,
                            "fats": float,
                            "key_nutrients": [string],
                            "alternatives": [
                                {
                                    "name": string,
                                    "portion": string,
                                    "calories": int
                                }
                            ]
                        }
                    ],
                    "notes": string
                }
            ],
            "special_instructions": string,
            "meal_prep_tips": string,
            "storage_guidelines": string
        }"""

        # Combine all sections into final prompt
        prompt = f"""You are an expert nutritionist AI. Generate a highly personalized diet plan based on the following user profile:

{user_profile}

{targets}

{requirements}

IMPORTANT: Your response must be a valid JSON object. Do not include any text before or after the JSON object.
Return ONLY the JSON object in this exact format:
{json_format}

Remember:
1. All strings must be properly escaped
2. All numbers must be integers or floats without quotes
3. Arrays must use square brackets []
4. Objects must use curly braces {{}}
5. No trailing commas
6. No comments or additional text"""

        # Get response from Gemini
        response = model.generate_content(prompt)
        if not response or not response.text:
            current_app.logger.error("No response received from Gemini")
            return get_fallback_diet_plan()
        
        # Parse and validate the response
        try:
            plan_text = response.text.strip()
            # Remove any markdown code block markers if present
            plan_text = plan_text.replace('```json', '').replace('```', '').strip()
            
            # Find the JSON object
            start = plan_text.find('{')
            end = plan_text.rfind('}') + 1
            if start >= 0 and end > start:
                plan_json = plan_text[start:end]
                try:
                    plan_data = json.loads(plan_json)
                    
                    # Validate the plan meets calorie and protein targets
                    total_calories = sum(
                        sum(food['calories'] for food in meal['foods'])
                        for meal in plan_data['meals']
                    )
                    if abs(total_calories - daily_calories) > 200:
                        current_app.logger.warning("Generated plan calories significantly differ from target")
                    
                    return plan_data
                except json.JSONDecodeError as e:
                    current_app.logger.error(f"JSON parsing error: {str(e)}")
                    current_app.logger.error(f"Raw JSON: {plan_json}")
                    return get_fallback_diet_plan()
            else:
                current_app.logger.error("No valid JSON object found in response")
                return get_fallback_diet_plan()
        except Exception as e:
            current_app.logger.error(f"Error parsing diet plan: {str(e)}")
            return get_fallback_diet_plan()
            
    except Exception as e:
        current_app.logger.error(f"Error generating diet plan: {str(e)}")
        return get_fallback_diet_plan()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_workout_plan(user, day_of_week=None, goal=None, activity_level=None, equipment=None):
    """Generate a personalized workout plan using Gemini AI"""
    try:
        model = init_gemini()
        if not model:
            current_app.logger.error("Failed to initialize Gemini model")
            return get_fallback_workout_plan()
        
        # Get user attributes
        user_age = getattr(user, 'age', 'Not specified')
        user_gender = getattr(user, 'gender', 'Not specified')
        user_fitness_goal = goal or getattr(user, 'fitness_goal', 'maintain')
        user_activity_level = activity_level or getattr(user, 'activity_level', 'beginner')
        user_equipment = equipment or 'none'
        user_health = getattr(user, 'health_conditions', 'None')
        
        # Build user profile section
        user_profile = f"""
        User Profile:
        - Age: {user_age}
        - Gender: {user_gender}
        - Fitness Goal: {user_fitness_goal}
        - Current Activity Level: {user_activity_level}
        - Available Equipment: {user_equipment}
        - Health Conditions: {user_health}"""

        # Define requirements section
        requirements = """
        Requirements:
        1. Create a COMPLETELY NEW and UNIQUE workout plan - DO NOT use templates
        2. Consider the user's age and any health conditions
        3. Progressive overload principles should be applied
        4. Include detailed form instructions and common mistakes to avoid
        5. Provide modifications for different fitness levels
        6. Include rest periods and intensity guidelines
        7. Add specific warm-up and cool-down routines
        8. Consider recovery needs based on age and fitness level
        9. Include mobility work appropriate for the workout
        10. Provide safety guidelines and precautions"""

        # Define JSON format
        json_format = """
        {
            "workout_type": string,
            "duration": int,
            "difficulty": string,
            "equipment_needed": [string],
            "target_areas": [string],
            "warm_up": [
                {
                    "exercise": string,
                    "duration": string,
                    "intensity": string,
                    "instructions": string,
                    "common_mistakes": [string]
                }
            ],
            "main_workout": [
                {
                    "exercise": string,
                    "sets": int,
                    "reps": string,
                    "tempo": string,
                    "rest": string,
                    "intensity": string,
                    "instructions": string,
                    "common_mistakes": [string],
                    "modifications": {
                        "easier": string,
                        "harder": string
                    },
                    "progression_tips": string
                }
            ],
            "cool_down": [
                {
                    "exercise": string,
                    "duration": string,
                    "intensity": string,
                    "instructions": string
                }
            ],
            "safety_guidelines": string,
            "recovery_recommendations": string,
            "progression_plan": string
        }"""

        # Combine all sections into final prompt
        prompt = f"""You are an expert fitness trainer AI. Generate a highly personalized workout plan based on the following user profile:

{user_profile}

{requirements}

IMPORTANT: Your response must be a valid JSON object. Do not include any text before or after the JSON object.
Return ONLY the JSON object in this exact format:
{json_format}

Remember:
1. All strings must be properly escaped
2. All numbers must be integers or floats without quotes
3. Arrays must use square brackets []
4. Objects must use curly braces {{}}
5. No trailing commas
6. No comments or additional text"""

        # Get response from Gemini
        response = model.generate_content(prompt)
        if not response or not response.text:
            current_app.logger.error("No response received from Gemini")
            return get_fallback_workout_plan()
        
        # Parse and validate the response
        try:
            plan_text = response.text.strip()
            # Remove any markdown code block markers if present
            plan_text = plan_text.replace('```json', '').replace('```', '').strip()
            
            # Find the JSON object
            start = plan_text.find('{')
            end = plan_text.rfind('}') + 1
            if start >= 0 and end > start:
                plan_json = plan_text[start:end]
                try:
                    plan_data = json.loads(plan_json)
                    
                    if (len(plan_data['warm_up']) < 2 or 
                        len(plan_data['main_workout']) < 3 or 
                        len(plan_data['cool_down']) < 2):
                        current_app.logger.warning("Generated plan may be incomplete")
                    
                    return plan_data
                except json.JSONDecodeError as e:
                    current_app.logger.error(f"JSON parsing error: {str(e)}")
                    current_app.logger.error(f"Raw JSON: {plan_json}")
                    return get_fallback_workout_plan()
            else:
                current_app.logger.error("No valid JSON object found in response")
                return get_fallback_workout_plan()
        except Exception as e:
            current_app.logger.error(f"Error parsing workout plan: {str(e)}")
            return get_fallback_workout_plan()
            
    except Exception as e:
        current_app.logger.error(f"Error generating workout plan: {str(e)}")
        return get_fallback_workout_plan()

def calculate_bmr(user):
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
    try:
        weight = float(getattr(user, 'weight', 70))
        height = float(getattr(user, 'height', 170))
        age = int(getattr(user, 'age', 30))
        gender = getattr(user, 'gender', '').lower()
        
        if gender == 'male':
            return (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            return (10 * weight) + (6.25 * height) - (5 * age) - 161
    except Exception as e:
        current_app.logger.error(f"Error calculating BMR: {str(e)}")
        return 1800  # Default value

def calculate_daily_calories(bmr, user):
    """Calculate daily calorie needs based on activity level and goals"""
    try:
        activity_multipliers = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extra_active': 1.9
        }
        
        activity_level = getattr(user, 'activity_level', 'moderately_active').lower()
        multiplier = activity_multipliers.get(activity_level, 1.55)
        maintenance_calories = bmr * multiplier
        
        goal_adjustments = {
            'lose_weight': -500,
            'gain_weight': 500,
            'build_muscle': 300,
            'maintain_weight': 0,
            'improve_endurance': 0
        }
        
        fitness_goal = getattr(user, 'fitness_goal', 'maintain_weight').lower()
        adjustment = goal_adjustments.get(fitness_goal, 0)
        
        return int(maintenance_calories + adjustment)
    except Exception as e:
        current_app.logger.error(f"Error calculating daily calories: {str(e)}")
        return 2000  # Default value

def calculate_protein_target(user, daily_calories):
    """Calculate daily protein target based on goals and body weight"""
    try:
        weight = float(getattr(user, 'weight', 70))
        fitness_goal = getattr(user, 'fitness_goal', 'maintain_weight').lower()
        
        protein_multipliers = {
            'lose_weight': 2.0,  # Higher protein for preserving muscle while cutting
            'gain_weight': 1.6,  # Moderate protein for bulking
            'build_muscle': 2.2,  # High protein for muscle growth
            'maintain_weight': 1.8,  # Moderate-high protein for maintenance
            'improve_endurance': 1.6  # Moderate protein for endurance
        }
        
        multiplier = protein_multipliers.get(fitness_goal, 1.8)
        return int(weight * multiplier)
    except Exception as e:
        current_app.logger.error(f"Error calculating protein target: {str(e)}")
        return 150  # Default value

def get_fallback_diet_plan():
    """Return a default diet plan when AI generation fails"""
    return {
        "daily_calories": 2000,
        "daily_protein": 150,
        "meals": [
            {
                "meal_type": "Breakfast",
                "suggested_time": "8:00 AM",
                "foods": [
                    {
                        "name": "Oatmeal with banana and almonds",
                        "preparation": "Cook oats with water or milk, slice banana, add almonds",
                        "portion": "1 cup oats, 1 medium banana, 10 almonds",
                        "calories": 350,
                        "protein": 12,
                        "carbs": 65,
                        "fats": 9,
                        "key_nutrients": ["Fiber", "Potassium", "Vitamin B6", "Magnesium"],
                        "alternatives": [
                            {
                                "name": "Greek yogurt with granola",
                                "portion": "1 cup yogurt, 1/2 cup granola",
                                "calories": 340
                            },
                            {
                                "name": "Whole grain toast with eggs",
                                "portion": "2 slices toast, 2 eggs",
                                "calories": 360
                            }
                        ]
                    }
                ],
                "notes": "Eat within 1 hour of waking up for optimal energy"
            },
            {
                "meal_type": "Lunch",
                "suggested_time": "1:00 PM",
                "foods": [
                    {
                        "name": "Grilled chicken salad",
                        "preparation": "Grill chicken breast, chop vegetables, toss with olive oil dressing",
                        "portion": "150g chicken, 2 cups mixed greens, 1 tbsp olive oil",
                        "calories": 400,
                        "protein": 35,
                        "carbs": 10,
                        "fats": 28,
                        "key_nutrients": ["Lean protein", "Vitamin C", "Iron", "Folate"],
                        "alternatives": [
                            {
                                "name": "Tuna sandwich",
                                "portion": "1 can tuna, 2 slices whole grain bread",
                                "calories": 380
                            },
                            {
                                "name": "Quinoa bowl with chickpeas",
                                "portion": "1 cup quinoa, 1/2 cup chickpeas",
                                "calories": 420
                            }
                        ]
                    }
                ],
                "notes": "Include colorful vegetables for maximum nutrients"
            }
        ],
        "special_instructions": "Adjust portions based on hunger levels while maintaining protein intake",
        "meal_prep_tips": "Prepare proteins and chop vegetables in advance for quicker assembly",
        "storage_guidelines": "Store prepared meals in airtight containers for up to 3 days"
    }

def get_fallback_workout_plan():
    """Return a default workout plan when AI generation fails"""
    return {
        "workout_type": "Full Body",
        "duration": 45,
        "difficulty": "Intermediate",
        "equipment_needed": ["None - Bodyweight only"],
        "target_areas": ["Full Body"],
        "warm_up": [
            {
                "exercise": "Light jogging in place",
                "duration": "5 minutes",
                "intensity": "Low",
                "instructions": "Start slow and gradually increase pace",
                "common_mistakes": [
                    "Starting too fast",
                    "Poor posture while jogging"
                ]
            },
            {
                "exercise": "Dynamic stretches",
                "duration": "5 minutes",
                "intensity": "Low to Moderate",
                "instructions": "Perform arm circles, leg swings, and hip rotations",
                "common_mistakes": [
                    "Stretching too quickly",
                    "Skipping major muscle groups"
                ]
            }
        ],
        "main_workout": [
            {
                "exercise": "Push-ups",
                "sets": 3,
                "reps": "10-12",
                "tempo": "2-1-2",
                "rest": "60 seconds",
                "intensity": "Moderate",
                "instructions": "Keep body straight, lower chest to ground",
                "common_mistakes": [
                    "Sagging hips",
                    "Incomplete range of motion"
                ],
                "modifications": {
                    "easier": "Wall push-ups or knee push-ups",
                    "harder": "Diamond push-ups or decline push-ups"
                },
                "progression_tips": "Increase reps before moving to harder variations"
            },
            {
                "exercise": "Bodyweight squats",
                "sets": 3,
                "reps": "15-20",
                "tempo": "2-1-1",
                "rest": "60 seconds",
                "intensity": "Moderate",
                "instructions": "Keep chest up, sink hips back and down",
                "common_mistakes": [
                    "Knees caving in",
                    "Heels lifting off ground"
                ],
                "modifications": {
                    "easier": "Supported squats holding onto a chair",
                    "harder": "Jump squats or pistol squats"
                },
                "progression_tips": "Focus on depth before adding dynamic movements"
            }
        ],
        "cool_down": [
            {
                "exercise": "Light walking",
                "duration": "3 minutes",
                "intensity": "Low",
                "instructions": "Walk at a comfortable pace to lower heart rate"
            },
            {
                "exercise": "Static stretching",
                "duration": "5 minutes",
                "intensity": "Low",
                "instructions": "Hold each stretch for 20-30 seconds"
            }
        ],
        "safety_guidelines": "Stop if you experience sharp pain, maintain proper form throughout",
        "recovery_recommendations": "Allow 24-48 hours between full body workouts",
        "progression_plan": "Increase reps or difficulty every 2-3 weeks as exercises become easier"
    }

def get_ai_response(user, question):
    """Get AI response to user questions"""
    try:
        model = init_gemini()
        if not model:
            return "I apologize, but I'm unable to process your question at the moment. Please try again later."
        
        prompt = f"""As a health and fitness expert, answer the following question:
        {question}
        
        Consider the user's context:
        - Fitness goal: {user.fitness_goal if hasattr(user, 'fitness_goal') else 'general fitness'}
        - Fitness level: {user.fitness_level if hasattr(user, 'fitness_level') else 'beginner'}
        """
        
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
        return "I apologize, but I couldn't generate a response. Please try asking your question differently."
        
    except Exception as e:
        current_app.logger.error(f"Error getting AI response: {str(e)}")
        return "I encountered an error while processing your question. Please try again later." 