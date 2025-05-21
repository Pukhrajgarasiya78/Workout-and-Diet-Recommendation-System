import os
import secrets
from datetime import timedelta

# Get the absolute path of the current directory
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    # Generate a random secret key if not set in environment
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # MongoDB configuration
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/diet_workout_db')
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # API Keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Debug mode
    DEBUG = True
    
    # Print the MongoDB URI for debugging
    print(f"MongoDB URI: {MONGO_URI}")
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Application settings
    POSTS_PER_PAGE = 10
    USERS_PER_PAGE = 20
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 