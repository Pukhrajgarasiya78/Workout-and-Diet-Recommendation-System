from flask_login import UserMixin
from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

class User(UserMixin):
    def __init__(self, user_data):
        self.user_data = user_data or {}
        
    @property
    def id(self):
        return str(self.user_data.get('_id'))
        
    @property
    def username(self):
        return self.user_data.get('username')
        
    @property
    def email(self):
        return self.user_data.get('email')
        
    @property
    def password_hash(self):
        return self.user_data.get('password_hash')
        
    @property
    def is_active(self):
        return self.user_data.get('is_active', True)
        
    @property
    def created_at(self):
        return self.user_data.get('created_at', datetime.utcnow())
        
    @property
    def updated_at(self):
        return self.user_data.get('updated_at', datetime.utcnow())
        
    @property
    def dietary_restrictions(self):
        return self.user_data.get('dietary_restrictions', [])
        
    @property
    def gender(self):
        return self.user_data.get('gender')
        
    @property
    def age(self):
        return self.user_data.get('age')
        
    @property
    def height(self):
        return self.user_data.get('height')
        
    @property
    def weight(self):
        return self.user_data.get('weight')
        
    @property
    def activity_level(self):
        return self.user_data.get('activity_level')
        
    @property
    def fitness_goal(self):
        return self.user_data.get('fitness_goal')
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'dietary_restrictions': self.dietary_restrictions,
            'gender': self.gender,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'activity_level': self.activity_level,
            'fitness_goal': self.fitness_goal
        }

    @property
    def profile(self):
        return {
            'first_name': self.user_data.get('first_name'),
            'last_name': self.user_data.get('last_name'),
            'age': self.user_data.get('age'),
            'gender': self.user_data.get('gender'),
            'weight': self.user_data.get('weight'),
            'height': self.user_data.get('height'),
            'activity_level': self.user_data.get('activity_level'),
            'fitness_goal': self.user_data.get('fitness_goal'),
            'dietary_preference': self.user_data.get('dietary_preference'),
            'health_conditions': self.user_data.get('health_conditions', '').split(','),
            'dietary_restrictions': self.user_data.get('dietary_restrictions', '').split(',')
        }
    
    @property
    def health_metrics(self):
        return {
            'bmi': self.user_data.get('bmi'),
            'bmr': self.user_data.get('bmr'),
            'daily_calorie_target': self.user_data.get('daily_calorie_target')
        }
    
    def check_password(self, password):
        return check_password_hash(self.user_data.get('password_hash', ''), password)
    
    @classmethod
    def create_user(cls, username, email, password, **kwargs):
        from app import mongo
        user_data = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True,
            **kwargs
        }
        result = mongo.db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return cls(user_data)
    
    @classmethod
    def get_by_username(cls, username):
        from app import mongo
        user_data = mongo.db.users.find_one({'username': username})
        return cls(user_data) if user_data else None
    
    @classmethod
    def get_by_email(cls, email):
        from app import mongo
        user_data = mongo.db.users.find_one({'email': email})
        return cls(user_data) if user_data else None
    
    def update_profile(self, **kwargs):
        from app import mongo
        updates = {
            '$set': {
                'updated_at': datetime.utcnow(),
                **kwargs
            }
        }
        mongo.db.users.update_one({'_id': ObjectId(self.id)}, updates)
        # Update the local user_data
        self.user_data.update(kwargs)
        self.user_data['updated_at'] = updates['$set']['updated_at']
    
    def get_diet_plans(self):
        from app import mongo
        return list(mongo.db.diet_plans.find({'user_id': self.id}))
    
    def get_workout_plans(self):
        from app import mongo
        return list(mongo.db.workout_plans.find({'user_id': self.id})) 