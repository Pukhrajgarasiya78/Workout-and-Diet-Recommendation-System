from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import mongo
from app.utils.ai_helper import generate_diet_plan, generate_workout_plan, get_ai_response, test_gemini_connection
from datetime import datetime, timedelta
import json
from app.forms.profile import ProfileForm

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('main/index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get today's date range
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Get user's daily goals
    daily_goals = mongo.db.daily_goals.find_one({
        'user_id': str(current_user.id),
        'date': today_start
    }) or {
        'calories': 2000,
        'protein': 150,
        'workout_minutes': 45
    }
    
    # Get today's food logs
    food_logs = list(mongo.db.meal_logs.find({
        'user_id': str(current_user.id),
        'created_at': {'$gte': today_start, '$lte': today_end}
    }).sort('created_at', -1))  # Sort by most recent first
    
    # Calculate total intake
    total_intake = {
        'calories': sum(log.get('total_calories', 0) for log in food_logs),
        'protein': sum(log.get('total_protein', 0) for log in food_logs),
        'carbs': sum(log.get('total_carbs', 0) for log in food_logs),
        'fats': sum(log.get('total_fats', 0) for log in food_logs)
    }
    
    # Get today's workout logs
    workout_logs = list(mongo.db.workout_logs.find({
        'user_id': str(current_user.id),
        'created_at': {'$gte': today_start, '$lte': today_end}
    }).sort('created_at', -1))  # Sort by most recent first
    
    # Calculate total workout stats
    total_workout = {
        'duration': sum(log.get('duration', 0) for log in workout_logs),
        'calories_burned': sum(log.get('calories_burned', 0) for log in workout_logs)
    }
    
    return render_template('main/dashboard.html',
        daily_goals=daily_goals,
        total_intake=total_intake,
        total_workout=total_workout,
        food_logs=food_logs,
        workout_logs=workout_logs
    )

@bp.route('/generate-diet-plan')
@login_required
def generate_diet():
    try:
        # Generate diet plan for the whole week
        for day in range(7):
            # Delete existing plans for this day
            mongo.db.diet_plans.delete_many({
                'user_id': current_user.id,
                'day_of_week': day
            })
            
            # Generate new plans for each meal type
            meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
            for meal_type in meal_types:
                plan_data = generate_diet_plan(
                    goal=current_user.profile.get('fitness_goal'),
                    restrictions=current_user.profile.get('dietary_restrictions', '').split(',')
                )
                
                plan = {
                    'user_id': current_user.id,
                    'day_of_week': day,
                    'meal_type': meal_type,
                    'calories': plan_data['calories'],
                    'protein': plan_data['protein'],
                    'carbs': plan_data['carbs'],
                    'fats': plan_data['fats'],
                    'meals': plan_data['meals'],
                    'notes': plan_data['notes'],
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
                mongo.db.diet_plans.insert_one(plan)
        
        flash('Diet plan generated successfully!', 'success')
    except Exception as e:
        flash(f'Error generating diet plan: {str(e)}', 'error')
    
    return redirect(url_for('main.dashboard'))

@bp.route('/generate-workout-plan')
@login_required
def generate_workout():
    try:
        # Generate workout plan for the whole week
        for day in range(7):
            # Delete existing plan for this day
            mongo.db.workout_plans.delete_one({
                'user_id': current_user.id,
                'day_of_week': day
            })
            
            # Generate new workout plan
            workout_data = generate_workout_plan(
                goal=current_user.profile.get('fitness_goal'),
                activity_level=current_user.profile.get('activity_level', 'beginner'),
                equipment='none'
            )
            
            plan = {
                'user_id': current_user.id,
                'day_of_week': day,
                'workout_type': workout_data['workout_type'],
                'duration': workout_data['duration'],
                'target_areas': workout_data['target_areas'],
                'warm_up': workout_data['warm_up'],
                'main_workout': workout_data['main_workout'],
                'cool_down': workout_data['cool_down'],
                'notes': workout_data['notes'],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            mongo.db.workout_plans.insert_one(plan)
        
        flash('Workout plan generated successfully!', 'success')
    except Exception as e:
        flash(f'Error generating workout plan: {str(e)}', 'error')
    
    return redirect(url_for('main.dashboard'))

@bp.route('/log-meal', methods=['POST'])
@login_required
def log_meal():
    data = request.json
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fats = 0
    food_items = []
    
    # Process each food item
    for i in range(len(data['food_items'])):
        food_item = data['food_items'][i]
        quantity = float(data['quantities'][i])
        unit = data['units'][i]
        
        # Get food data from database
        food_data = mongo.db.food_database.find_one({
            'name': {'$regex': f'^{food_item}$', '$options': 'i'}
        })
        
        if not food_data:
            return jsonify({
                'status': 'error',
                'message': f'Food item "{food_item}" not found in database'
            }), 404
        
        # Convert quantity to standard unit (grams or ml)
        std_quantity = convert_to_standard_unit(quantity, unit, food_data)
        
        # Calculate nutritional values based on quantity
        multiplier = std_quantity / food_data['serving_size']
        calories = round(food_data['calories'] * multiplier)
        protein = round(food_data['protein'] * multiplier, 1)
        carbs = round(food_data['carbs'] * multiplier, 1)
        fats = round(food_data['fats'] * multiplier, 1)
        
        # Add to totals
        total_calories += calories
        total_protein += protein
        total_carbs += carbs
        total_fats += fats
        
        # Store individual food item
        food_items.append({
            'food_item': food_item,
            'quantity': quantity,
            'unit': unit if unit != 'none' else '',  # Don't show 'none' in the log
            'calories': calories,
            'protein': protein,
            'carbs': carbs,
            'fats': fats
        })
    
    # Create meal log
    meal = {
        'user_id': str(current_user.id),
        'meal_type': data['meal_type'],
        'food_items': food_items,
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fats': total_fats,
        'created_at': datetime.now()
    }
    
    # Insert the meal log
    mongo.db.meal_logs.insert_one(meal)
    
    # Calculate remaining calories and protein
    daily_goals = mongo.db.daily_goals.find_one({
        'user_id': str(current_user.id),
        'date': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    }) or {'calories': 2000, 'protein': 150}
    
    total_intake = mongo.db.meal_logs.aggregate([
        {
            '$match': {
                'user_id': str(current_user.id),
                'created_at': {
                    '$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                }
            }
        },
        {
            '$group': {
                '_id': None,
                'total_calories': {'$sum': '$total_calories'},
                'total_protein': {'$sum': '$total_protein'}
            }
        }
    ]).next()
    
    remaining = {
        'calories': daily_goals['calories'] - total_intake['total_calories'],
        'protein': daily_goals['protein'] - total_intake['total_protein']
    }
    
    return jsonify({
        'status': 'success',
        'meal': meal,
        'remaining': remaining
    })

def convert_to_standard_unit(quantity, unit, food_data):
    """Convert quantity from common units to grams/ml"""
    # Handle unit-less foods
    if unit == 'none':
        # For foods that don't need units (like roti, chapati, bread slice)
        return quantity * food_data.get('weight_per_piece', 50)  # Default to 50g if not specified
    
    conversions = {
        'piece': lambda q, f: q * f.get('weight_per_piece', 0),
        'bowl': lambda q, f: q * f.get('weight_per_bowl', 200),  # Default bowl size
        'plate': lambda q, f: q * f.get('weight_per_plate', 300),  # Default plate size
        'cup': lambda q, f: q * f.get('weight_per_cup', 240),  # Standard cup size
        'tablespoon': lambda q, f: q * f.get('weight_per_tbsp', 15),
        'teaspoon': lambda q, f: q * f.get('weight_per_tsp', 5),
        'grams': lambda q, f: q,
        'ml': lambda q, f: q,
        'scoop': lambda q, f: q * f.get('weight_per_scoop', 30),
        'serving': lambda q, f: q * f.get('weight_per_serving', 100),
        'glass': lambda q, f: q * f.get('weight_per_glass', 240),
        'katori': lambda q, f: q * f.get('weight_per_katori', 150)
    }
    
    if unit.lower() in conversions:
        return conversions[unit.lower()](quantity, food_data)
    return quantity  # Default to assuming grams/ml

@bp.route('/log-workout', methods=['POST'])
@login_required
def log_workout():
    try:
        data = request.json
        
        # Get user's weight (default to 70kg if not set)
        user_weight = 70  # Default weight
        if hasattr(current_user, 'profile') and current_user.profile:
            profile_weight = current_user.profile.get('weight')
            if profile_weight is not None:
                try:
                    user_weight = float(profile_weight)
                except (ValueError, TypeError):
                    pass
        
        total_duration = 0
        total_calories_burned = 0
        workout_logs = []
        
        # Process each exercise
        for exercise in data['exercises']:
            # Get exercise data from database
            exercise_data = mongo.db.exercise_database.find_one({
                'name': {'$regex': f'^{exercise["exercise_name"]}$', '$options': 'i'}
            })
            
            if not exercise_data:
                return jsonify({
                    'status': 'error',
                    'message': f'Exercise "{exercise["exercise_name"]}" not found in database'
                }), 404
            
            # Calculate calories burned based on MET value
            duration_hours = float(exercise['duration']) / 60  # Convert minutes to hours
            calories_burned = round(float(exercise_data['met']) * user_weight * duration_hours)
            
            # Create workout log
            workout = {
                'user_id': str(current_user.id),
                'exercise_name': exercise['exercise_name'],
                'duration': int(exercise['duration']),
                'calories_burned': calories_burned,
                'created_at': datetime.now()
            }
            
            # Insert the workout log
            mongo.db.workout_logs.insert_one(workout)
            workout_logs.append(workout)
            
            # Add to totals
            total_duration += int(exercise['duration'])
            total_calories_burned += calories_burned
        
        # Get daily goals
        daily_goals = mongo.db.daily_goals.find_one({
            'user_id': str(current_user.id),
            'date': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        }) or {'workout_minutes': 45}
        
        # Calculate totals for today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        total_workout = mongo.db.workout_logs.aggregate([
            {
                '$match': {
                    'user_id': str(current_user.id),
                    'created_at': {'$gte': today_start, '$lte': today_end}
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total_duration': {'$sum': '$duration'},
                    'total_calories_burned': {'$sum': '$calories_burned'}
                }
            }
        ]).next()
        
        return jsonify({
            'status': 'success',
            'workouts': workout_logs,
            'remaining': {
                'workout_minutes': daily_goals['workout_minutes'] - total_workout['total_duration'],
                'calories_burned': total_workout['total_calories_burned']
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error logging workout: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while logging the workout'
        }), 500

@bp.route('/log-water', methods=['POST'])
@login_required
def log_water():
    data = request.json
    water = {
        'user_id': current_user.id,
        'amount': data['amount'],
        'created_at': datetime.utcnow()
    }
    mongo.db.water_logs.insert_one(water)
    return jsonify({'status': 'success'})

@bp.route('/update-progress', methods=['POST'])
@login_required
def update_progress():
    data = request.json
    progress = {
        'user_id': current_user.id,
        'weight': data['weight'],
        'body_fat': data.get('body_fat'),
        'muscle_mass': data.get('muscle_mass'),
        'waist': data.get('waist'),
        'chest': data.get('chest'),
        'arms': data.get('arms'),
        'thighs': data.get('thighs'),
        'notes': data.get('notes', ''),
        'created_at': datetime.utcnow()
    }
    mongo.db.progress_updates.insert_one(progress)
    
    # Update user's weight in profile
    mongo.db.users.update_one(
        {'_id': current_user.user_data['_id']},
        {'$set': {
            'weight': data['weight'],
            'updated_at': datetime.utcnow()
        }}
    )
    
    return jsonify({'status': 'success'})

@bp.route('/ask-ai', methods=['POST'])
@login_required
def ask_ai():
    data = request.json
    question = data['question']
    response = get_ai_response(current_user, question)
    return jsonify({'response': response})

@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    return render_template('main/profile.html', form=form)

@bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        # Update user data in MongoDB
        update_data = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'email': form.email.data,
            'age': form.age.data,
            'weight': form.weight.data,
            'height': form.height.data,
            'gender': form.gender.data,
            'activity_level': form.activity_level.data,
            'fitness_goal': form.fitness_goal.data,
            'dietary_preference': form.dietary_preference.data,
            'health_conditions': form.health_conditions.data.split(',') if form.health_conditions.data else [],
            'dietary_restrictions': form.dietary_restrictions.data.split(',') if form.dietary_restrictions.data else [],
            'updated_at': datetime.utcnow()
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        mongo.db.users.update_one(
            {'_id': current_user._id},
            {'$set': update_data}
        )
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    
    flash('Error updating profile. Please check your inputs.', 'danger')
    return redirect(url_for('main.profile'))

@bp.route('/test-gemini')
@login_required
def test_gemini():
    """Test route to verify Gemini API connection"""
    success, message = test_gemini_connection()
    return jsonify({
        'success': success,
        'message': message
    }) 