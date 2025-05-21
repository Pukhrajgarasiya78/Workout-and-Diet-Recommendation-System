from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class DietPlanForm(FlaskForm):
    goal = SelectField('Goal', choices=[
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintenance', 'Maintenance'),
        ('health_improvement', 'Health Improvement')
    ], validators=[DataRequired()])
    preferences = TextAreaField('Additional Preferences')
    submit = SubmitField('Generate Plan')

class WorkoutPlanForm(FlaskForm):
    fitness_goal = SelectField('Fitness Goal', choices=[
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('endurance', 'Improve Endurance'),
        ('strength', 'Build Strength'),
        ('flexibility', 'Increase Flexibility')
    ], validators=[DataRequired()])
    fitness_level = SelectField('Fitness Level', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], validators=[DataRequired()])
    notes = TextAreaField('Additional Notes')
    submit = SubmitField('Generate Plan') 