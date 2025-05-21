from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app.models.user import User
from app.forms.auth import LoginForm, RegistrationForm, ProfileForm
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
from datetime import datetime

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Check if username or email already exists
        if mongo.db.users.find_one({'username': username}):
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))
        
        if mongo.db.users.find_one({'email': email}):
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user_data = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        try:
            mongo.db.users.insert_one(user_data)
            user = User(user_data)
            login_user(user)
            flash('Registration successful!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            flash('An error occurred during registration', 'error')
            print(f"Registration error: {str(e)}")
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user_data = mongo.db.users.find_one({'username': form.username.data})
        if user_data:
            user = User(user_data)
            if user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash('Logged in successfully!', 'success')
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('main.index')
                return redirect(next_page)
        
        flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/complete-profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        updates = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'age': form.age.data,
            'gender': form.gender.data,
            'weight': form.weight.data,
            'height': form.height.data,
            'activity_level': form.activity_level.data,
            'fitness_goal': form.fitness_goal.data,
            'dietary_preference': form.dietary_preference.data,
            'health_conditions': form.health_conditions.data,
            'dietary_restrictions': form.dietary_restrictions.data,
            'updated_at': datetime.utcnow()
        }
        
        try:
            mongo.db.users.update_one(
                {'_id': current_user.user_data['_id']},
                {'$set': updates}
            )
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            flash('An error occurred while updating profile', 'error')
            print(f"Profile update error: {str(e)}")
        
        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/complete_profile.html', title='Complete Profile', form=form)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if request.method == 'GET':
        # Pre-populate form with current user data
        form.first_name.data = current_user.user_data.get('first_name')
        form.last_name.data = current_user.user_data.get('last_name')
        form.age.data = current_user.user_data.get('age')
        form.gender.data = current_user.user_data.get('gender')
        form.weight.data = current_user.user_data.get('weight')
        form.height.data = current_user.user_data.get('height')
        form.activity_level.data = current_user.user_data.get('activity_level')
        form.fitness_goal.data = current_user.user_data.get('fitness_goal')
        form.dietary_preference.data = current_user.user_data.get('dietary_preference')
        form.health_conditions.data = current_user.user_data.get('health_conditions')
        form.dietary_restrictions.data = current_user.user_data.get('dietary_restrictions')
    
    if form.validate_on_submit():
        updates = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'age': form.age.data,
            'gender': form.gender.data,
            'weight': form.weight.data,
            'height': form.height.data,
            'activity_level': form.activity_level.data,
            'fitness_goal': form.fitness_goal.data,
            'dietary_preference': form.dietary_preference.data,
            'health_conditions': form.health_conditions.data,
            'dietary_restrictions': form.dietary_restrictions.data,
            'updated_at': datetime.utcnow()
        }
        
        try:
            mongo.db.users.update_one(
                {'_id': current_user.user_data['_id']},
                {'$set': updates}
            )
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            flash('An error occurred while updating profile', 'error')
            print(f"Profile update error: {str(e)}")
        
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', form=form) 