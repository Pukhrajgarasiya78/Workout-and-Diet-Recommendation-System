from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import mongo
from app.utils.ai_helper import generate_diet_plan
from cryptography.fernet import Fernet
import json
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired

bp = Blueprint('diet', __name__)

# Use the same encryption functions as workout.py
def get_encryption_key():
    return current_app.config.get('ENCRYPTION_KEY', Fernet.generate_key())

def encrypt_data(data):
    f = Fernet(get_encryption_key())
    return f.encrypt(json.dumps(data).encode())

def decrypt_data(encrypted_data):
    f = Fernet(get_encryption_key())
    return json.loads(f.decrypt(encrypted_data).decode())

class DietPlanForm(FlaskForm):
    day = SelectField('Day of Week', choices=[
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], validators=[DataRequired()])
    
    meal_type = SelectField('Meal Type', choices=[
        ('all', 'All Meals'),
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snacks', 'Snacks')
    ], validators=[DataRequired()])
    
    restrictions = TextAreaField('Dietary Restrictions')

@bp.route('/diet', methods=['GET'])
@login_required
def index():
    form = DietPlanForm()
    return render_template('diet/index.html', form=form)

@bp.route('/diet/log', methods=['POST'])
@login_required
def log_meal():
    try:
        data = request.json
        meal = {
            'user_id': current_user.id,
            'meal_type': data['meal_type'],
            'food_item': data['food_item'],
            'portion_size': data['portion_size'],
            'calories': data['calories'],
            'protein': data.get('protein', 0),
            'carbs': data.get('carbs', 0),
            'fats': data.get('fats', 0),
            'notes': data.get('notes', ''),
            'created_at': datetime.utcnow()
        }
        mongo.db.meal_logs.insert_one(meal)
        return jsonify({'status': 'success'})
    except Exception as e:
        current_app.logger.error(f"Error logging meal: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/diet/generate', methods=['GET', 'POST'])
@login_required
def generate():
    try:
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data received'}), 400
                
            day = int(data.get('day', 0))
            meal_type = data.get('meal_type', 'all')
            restrictions = data.get('restrictions', '')
            goal = data.get('goal', current_user.profile.get('fitness_goal', 'weight_loss'))
            
            # Update user's dietary preference before generating plan
            current_user.dietary_preference = restrictions
            
            # Generate new diet plan
            plan_data = generate_diet_plan(current_user)
            if not plan_data:
                return jsonify({'error': 'Failed to generate diet plan'}), 500
            
            # Store the plan in MongoDB
            plan_doc = {
                'user_id': current_user.id,
                'day_of_week': day,
                'meal_type': meal_type,
                'plan_data': encrypt_data(plan_data),
                'created_at': datetime.utcnow()
            }
            
            # Check if a plan already exists for this day
            existing_plan = mongo.db.diet_plans.find_one({
                'user_id': current_user.id,
                'day_of_week': day
            })
            
            if existing_plan:
                # Update existing plan
                mongo.db.diet_plans.update_one(
                    {'_id': existing_plan['_id']},
                    {'$set': plan_doc}
                )
            else:
                # Insert new plan
                mongo.db.diet_plans.insert_one(plan_doc)
            
            return jsonify(plan_data)
            
        else:  # GET request
            day = int(request.args.get('day', 0))
            meal_type = request.args.get('meal_type', 'all')
            
            # Retrieve existing plan
            plan = mongo.db.diet_plans.find_one({
                'user_id': current_user.id,
                'day_of_week': day
            })
            
            if plan:
                plan_data = decrypt_data(plan['plan_data'])
                return jsonify(plan_data)
            else:
                return jsonify({
                    'error': 'No plan found for this day'
                }), 404
                
    except Exception as e:
        current_app.logger.error(f"Error in diet plan generation: {str(e)}")
        return jsonify({
            'error': 'Failed to generate or retrieve diet plan',
            'message': str(e)
        }), 500

@bp.route('/diet/history')
@login_required
def history():
    try:
        # Get all diet plans for the user
        plans = list(mongo.db.diet_plans.find({
            'user_id': current_user.id
        }).sort('created_at', -1))
        
        # Decrypt plan data
        for plan in plans:
            plan['plan_data'] = decrypt_data(plan['plan_data'])
        
        return render_template('diet/history.html', plans=plans)
    except Exception as e:
        current_app.logger.error(f"Error retrieving diet history: {str(e)}")
        flash('Error retrieving diet history', 'error')
        return redirect(url_for('diet.index')) 