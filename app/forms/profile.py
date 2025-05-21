from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, SelectField, StringField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Optional, NumberRange, Email

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[Optional()])
    last_name = StringField('Last Name', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    age = IntegerField('Age', validators=[Optional(), NumberRange(min=1, max=120)])
    weight = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=1, max=500)])
    height = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=1, max=300)])
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[Optional()])
    activity_level = SelectField('Activity Level', choices=[
        ('', 'Select Activity Level'),
        ('sedentary', 'Sedentary'),
        ('lightly_active', 'Lightly Active'),
        ('moderately_active', 'Moderately Active'),
        ('very_active', 'Very Active'),
        ('extra_active', 'Extra Active')
    ], validators=[Optional()])
    fitness_goal = SelectField('Fitness Goal', choices=[
        ('', 'Select Fitness Goal'),
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintain', 'Maintain Weight'),
        ('improve_fitness', 'Improve Fitness'),
        ('increase_strength', 'Increase Strength')
    ], validators=[Optional()])
    dietary_preference = SelectField('Dietary Preference', choices=[
        ('', 'Select Dietary Preference'),
        ('omnivore', 'Omnivore'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('pescatarian', 'Pescatarian'),
        ('keto', 'Ketogenic'),
        ('paleo', 'Paleo')
    ], validators=[Optional()])
    health_conditions = TextAreaField('Health Conditions (comma-separated)', validators=[Optional()])
    dietary_restrictions = TextAreaField('Dietary Restrictions (comma-separated)', validators=[Optional()]) 