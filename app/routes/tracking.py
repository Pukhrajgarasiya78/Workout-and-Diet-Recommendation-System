from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app import mongo
from bson import ObjectId
from app.utils.ai_helper import generate_diet_plan, generate_workout_plan

bp = Blueprint('tracking', __name__)

@bp.route('/api/daily-goals', methods=['GET'])
@login_required
def get_daily_goals():
    try:
        # Get user's profile data
        user_profile = mongo.db.users.find_one({'_id': current_user.id})
        
        # Get or generate daily goals using Gemini
        goals = mongo.db.daily_goals.find_one({
            'user_id': current_user.id,
            'date': datetime.utcnow().strftime('%Y-%m-%d')
        })
        
        if not goals:
            # Generate new goals using AI
            diet_plan = generate_diet_plan(current_user)
            workout_plan = generate_workout_plan(current_user)
            
            goals = {
                'user_id': current_user.id,
                'date': datetime.utcnow().strftime('%Y-%m-%d'),
                'target_calories': diet_plan.get('daily_calories', 2000),
                'target_protein': diet_plan.get('daily_protein', 150),
                'target_workout_duration': workout_plan.get('duration', 60),
                'created_at': datetime.utcnow()
            }
            mongo.db.daily_goals.insert_one(goals)
        
        return jsonify({
            'status': 'success',
            'goals': {
                'target_calories': goals['target_calories'],
                'target_protein': goals['target_protein'],
                'target_workout_duration': goals['target_workout_duration']
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error getting daily goals: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get daily goals'
        }), 500

@bp.route('/api/diet/log', methods=['POST'])
@login_required
def log_food():
    try:
        data = request.json
        log_entry = {
            'user_id': current_user.id,
            'food_name': data['food_name'],
            'portion_size': data['portion_size'],
            'calories': data['calories'],
            'protein': data.get('protein', 0),
            'created_at': datetime.utcnow()
        }
        
        # Insert the log entry
        mongo.db.diet_logs.insert_one(log_entry)
        
        # Calculate daily totals
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_logs = mongo.db.diet_logs.find({
            'user_id': current_user.id,
            'created_at': {'$gte': today}
        })
        
        total_calories = sum(log.get('calories', 0) for log in daily_logs)
        total_protein = sum(log.get('protein', 0) for log in daily_logs)
        
        # Get daily goals
        goals = mongo.db.daily_goals.find_one({
            'user_id': current_user.id,
            'date': today.strftime('%Y-%m-%d')
        })
        
        target_calories = goals['target_calories'] if goals else 2000
        remaining_calories = max(0, target_calories - total_calories)
        target_met = total_calories >= target_calories
        
        return jsonify({
            'status': 'success',
            'daily_total': {
                'calories': total_calories,
                'protein': total_protein,
                'remaining_calories': remaining_calories,
                'target_met': target_met
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error logging food: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to log food'
        }), 500

@bp.route('/api/workout/log', methods=['POST'])
@login_required
def log_workout():
    try:
        data = request.json
        log_entry = {
            'user_id': current_user.id,
            'exercise_name': data['exercise_name'],
            'duration': data['duration'],
            'calories_burned': data['calories_burned'],
            'completed': data.get('completed', True),
            'created_at': datetime.utcnow()
        }
        
        # Insert the log entry
        mongo.db.workout_logs.insert_one(log_entry)
        
        # Calculate daily totals
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_logs = mongo.db.workout_logs.find({
            'user_id': current_user.id,
            'created_at': {'$gte': today}
        })
        
        total_duration = sum(log.get('duration', 0) for log in daily_logs)
        total_calories_burned = sum(log.get('calories_burned', 0) for log in daily_logs)
        
        # Get daily goals
        goals = mongo.db.daily_goals.find_one({
            'user_id': current_user.id,
            'date': today.strftime('%Y-%m-%d')
        })
        
        target_duration = goals['target_workout_duration'] if goals else 60
        remaining_duration = max(0, target_duration - total_duration)
        target_met = total_duration >= target_duration
        
        return jsonify({
            'status': 'success',
            'daily_total': {
                'duration': total_duration,
                'calories_burned': total_calories_burned,
                'remaining_duration': remaining_duration,
                'target_met': target_met
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error logging workout: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to log workout'
        }), 500

@bp.route('/api/progress/today', methods=['GET'])
@login_required
def get_today_progress():
    try:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get daily goals
        goals = mongo.db.daily_goals.find_one({
            'user_id': current_user.id,
            'date': today.strftime('%Y-%m-%d')
        })
        
        if not goals:
            # Generate new goals using AI
            diet_plan = generate_diet_plan(current_user)
            workout_plan = generate_workout_plan(current_user)
            
            goals = {
                'user_id': current_user.id,
                'date': today.strftime('%Y-%m-%d'),
                'target_calories': diet_plan.get('daily_calories', 2000),
                'target_protein': diet_plan.get('daily_protein', 150),
                'target_workout_duration': workout_plan.get('duration', 60),
                'created_at': datetime.utcnow()
            }
            mongo.db.daily_goals.insert_one(goals)
        
        # Get diet logs
        diet_logs = list(mongo.db.diet_logs.find({
            'user_id': current_user.id,
            'created_at': {'$gte': today}
        }).sort('created_at', -1))
        
        total_calories = sum(log.get('calories', 0) for log in diet_logs)
        total_protein = sum(log.get('protein', 0) for log in diet_logs)
        remaining_calories = max(0, goals['target_calories'] - total_calories)
        diet_target_met = total_calories >= goals['target_calories']
        
        # Get workout logs
        workout_logs = list(mongo.db.workout_logs.find({
            'user_id': current_user.id,
            'created_at': {'$gte': today}
        }).sort('created_at', -1))
        
        total_duration = sum(log.get('duration', 0) for log in workout_logs)
        total_calories_burned = sum(log.get('calories_burned', 0) for log in workout_logs)
        remaining_duration = max(0, goals['target_workout_duration'] - total_duration)
        workout_target_met = total_duration >= goals['target_workout_duration']
        
        # Convert ObjectId to string for JSON serialization
        for log in diet_logs:
            log['_id'] = str(log['_id'])
        for log in workout_logs:
            log['_id'] = str(log['_id'])
        
        return jsonify({
            'status': 'success',
            'goals': {
                'target_calories': goals['target_calories'],
                'target_protein': goals['target_protein'],
                'target_workout_duration': goals['target_workout_duration']
            },
            'progress': {
                'diet': {
                    'total_calories': total_calories,
                    'total_protein': total_protein,
                    'remaining_calories': remaining_calories,
                    'target_met': diet_target_met
                },
                'workout': {
                    'total_duration': total_duration,
                    'total_calories_burned': total_calories_burned,
                    'remaining_duration': remaining_duration,
                    'target_met': workout_target_met
                }
            },
            'logs': {
                'diet': diet_logs,
                'workout': workout_logs
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error getting today's progress: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get progress'
        }), 500 