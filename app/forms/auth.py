from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange, ValidationError
from app import mongo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = mongo.db.users.find_one({'username': username.data})
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = mongo.db.users.find_one({'email': email.data})
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[Optional(), Length(max=64)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=64)])
    age = IntegerField('Age', validators=[Optional(), NumberRange(min=13, max=120)])
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], validators=[Optional()])
    weight = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=20, max=300)])
    height = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=100, max=250)])
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
        ('lose_weight', 'Lose Weight'),
        ('maintain_weight', 'Maintain Weight'),
        ('gain_weight', 'Gain Weight'),
        ('build_muscle', 'Build Muscle'),
        ('improve_endurance', 'Improve Endurance')
    ], validators=[Optional()])
    dietary_preference = SelectField('Dietary Preference', choices=[
        ('', 'Select Dietary Preference'),
        ('none', 'No Specific Preference'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('pescatarian', 'Pescatarian'),
        ('keto', 'Ketogenic'),
        ('paleo', 'Paleo')
    ], validators=[Optional()])
    health_conditions = TextAreaField('Health Conditions', validators=[Optional(), Length(max=500)])
    dietary_restrictions = TextAreaField('Dietary Restrictions', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Profile') 