from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import mongo
from app.utils.ai_helper import generate_workout_plan
from cryptography.fernet import Fernet
import json
from datetime import datetime

bp = Blueprint('workout', __name__)

# Initialize encryption key (store this securely in environment variables)
def get_encryption_key():
    return current_app.config.get('ENCRYPTION_KEY', Fernet.generate_key())

def encrypt_data(data):
    f = Fernet(get_encryption_key())
    return f.encrypt(json.dumps(data).encode())

def decrypt_data(encrypted_data):
    f = Fernet(get_encryption_key())
    return json.loads(f.decrypt(encrypted_data).decode())

@bp.route('/workout', methods=['GET'])
@login_required
def index():
    return render_template('workout/index.html')

@bp.route('/workout/log', methods=['POST'])
@login_required
def log_workout():
    data = request.json
    workout = {
        'user_id': current_user.id,
        'workout_type': data['workout_type'],
        'exercise_name': data['exercise_name'],
        'duration': data['duration'],
        'sets': data.get('sets'),
        'reps': data.get('reps'),
        'weight': data.get('weight'),
        'calories_burned': data.get('calories_burned'),
        'notes': data.get('notes', ''),
        'created_at': datetime.utcnow()
    }
    mongo.db.workout_logs.insert_one(workout)
    return jsonify({'status': 'success'})

@bp.route('/workout/generate', methods=['POST'])
@login_required
def generate():
    """Generate a new workout plan"""
    try:
        current_app.logger.info("Generating new workout plan...")
        
        # Get current user
        user = current_user
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
            
        # Get form data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
            
        # Extract parameters from form data
        day_of_week = int(data.get('day', 0))
        goal = data.get('goal')
        activity_level = data.get('activity_level')
        equipment = data.get('equipment')
            
        # Log user data for debugging
        current_app.logger.debug(f"Current user attributes: {user.__dict__}")
        current_app.logger.debug(f"Form data: {data}")
        
        # Generate workout plan with form data
        workout_data = generate_workout_plan(
            user=user,
            day_of_week=day_of_week,
            goal=goal,
            activity_level=activity_level,
            equipment=equipment
        )
        
        if not workout_data:
            current_app.logger.error("Failed to generate workout plan")
            return jsonify({'error': 'Failed to generate workout plan'}), 500
            
        current_app.logger.debug(f"Generated workout data: {workout_data}")
        
        # Save to database
        workout_collection = mongo.db.workout_plans
        
        # Check if plan exists for user and day
        existing_plan = workout_collection.find_one({
            'user_id': user.id,
            'day_of_week': day_of_week
        })
        
        plan_data = {
            'user_id': user.id,
            'day_of_week': day_of_week,
            'plan': workout_data,
            'updated_at': datetime.utcnow()
        }
        
        if existing_plan:
            current_app.logger.info("Updating existing plan...")
            result = workout_collection.update_one(
                {'_id': existing_plan['_id']},
                {'$set': plan_data}
            )
            current_app.logger.info(f"Update result: {result.modified_count} document(s) modified")
        else:
            current_app.logger.info("Creating new plan...")
            plan_data['created_at'] = datetime.utcnow()
            workout_collection.insert_one(plan_data)
        
        current_app.logger.info("Successfully saved workout plan to database")
        return jsonify({
            'success': True,
            'message': 'Workout plan generated successfully',
            'data': workout_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in generate_workout: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/workout/history')
@login_required
def history():
    plans = list(mongo.db.workout_plans.find({'user_id': current_user.id}))
    return render_template('workout/history.html', plans=plans) 