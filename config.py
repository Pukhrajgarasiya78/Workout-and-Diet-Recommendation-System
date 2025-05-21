import os
import secrets
from dotenv import load_dotenv
from datetime import timedelta

# Get the absolute path of the current directory
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Load environment variables from .env file
load_dotenv(os.path.join(project_root, '.env'))

# Ensure the instance directory exists
os.makedirs(os.path.join(project_root, 'instance'), exist_ok=True)

class Config:
    # Generate a random secret key if not set in environment
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # MongoDB configuration
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/diet_workout_db')
    MONGO_CONNECT = True
    MONGO_CONNECT_TIMEOUT_MS = 30000
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_TYPE = 'filesystem'
    
    # API Keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it to use the AI features.")
    
    # Debug mode
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
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

    # Additional MongoDB settings
    MONGO_TLS = True
    MONGO_TLS_ALLOW_INVALID_CERTIFICATES = True
    MONGO_RETRY_WRITES = True
    MONGO_W = 'majority'
    MONGO_MAX_POOL_SIZE = 100
    MONGO_MIN_POOL_SIZE = 0
    MONGO_MAX_IDLE_TIME_MS = 10000
    MONGO_SERVER_SELECTION_TIMEOUT_MS = 30000
    
    # API Keys
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Application settings
    POSTS_PER_PAGE = 10
    USERS_PER_PAGE = 20
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 