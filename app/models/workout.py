from datetime import datetime
from app import db

class WorkoutPlan(db.Model):
    __tablename__ = 'workout_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0 = Monday, 6 = Sunday
    workout_type = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    target_areas = db.Column(db.String(200), nullable=False)  # comma-separated list
    warm_up = db.Column(db.Text, nullable=False)  # stored as string representation of list
    main_workout = db.Column(db.Text, nullable=False)  # stored as string representation of list
    cool_down = db.Column(db.Text, nullable=False)  # stored as string representation of list
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with User model
    user = db.relationship('User', backref=db.backref('workout_plans', lazy=True))
    
    def __repr__(self):
        return f'<WorkoutPlan {self.id} for user {self.user_id} on day {self.day_of_week}>' 