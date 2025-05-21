from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    # Profile information
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    gender = db.Column(db.String(10))
    activity_level = db.Column(db.String(20))
    fitness_goal = db.Column(db.String(20))
    dietary_restrictions = db.Column(db.String(200))
    
    # Relationships
    diet_plans = db.relationship('DietPlan', backref='user', lazy=True)
    workout_plans = db.relationship('WorkoutPlan', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class DietPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Plan details
    calories = db.Column(db.Integer)
    protein = db.Column(db.Integer)
    carbs = db.Column(db.Integer)
    fats = db.Column(db.Integer)
    meals = db.Column(db.JSON)
    notes = db.Column(db.Text)

class WorkoutPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0 = Monday, 6 = Sunday
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Plan details
    workout_type = db.Column(db.String(50))
    duration = db.Column(db.Integer)  # in minutes
    target_areas = db.Column(db.JSON)  # List of target muscle groups
    warm_up = db.Column(db.JSON)  # List of warm-up exercises
    main_workout = db.Column(db.JSON)  # List of main exercises
    cool_down = db.Column(db.JSON)  # List of cool-down exercises
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'day_of_week': self.day_of_week,
            'workout_type': self.workout_type,
            'duration': self.duration,
            'target_areas': self.target_areas,
            'warm_up': self.warm_up,
            'main_workout': self.main_workout,
            'cool_down': self.cool_down,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 