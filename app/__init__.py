import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from bson import ObjectId
import logging
from logging.handlers import RotatingFileHandler
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
from app.utils.food_database import initialize_food_database
from app.utils.exercise_database import initialize_exercise_database

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
mongo = PyMongo()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()
scheduler = BackgroundScheduler()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        from app.config import Config
        config_class = Config
    
    app.config.from_object(config_class)
    
    # Ensure required environment variables are set
    if not app.config.get('GEMINI_API_KEY'):
        app.logger.error("GEMINI_API_KEY not found in environment variables")
        raise ValueError("GEMINI_API_KEY must be set")
    
    # Configure logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/diet_workout.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Diet Workout App startup')

    # Initialize MongoDB with error handling
    try:
        mongo.init_app(app)
        # Test the connection
        mongo.db.command('ping')
        app.logger.info('MongoDB connection successful')
        
        # Create collections if they don't exist
        collections = mongo.db.list_collection_names()
        required_collections = [
            'users', 'workout_plans', 'diet_plans', 'diet_logs', 
            'workout_logs', 'daily_goals', 'meal_logs', 'water_logs', 
            'progress_updates', 'food_database', 'exercise_database'
        ]
        
        for collection in required_collections:
            if collection not in collections:
                mongo.db.create_collection(collection)
                app.logger.info(f"Created {collection} collection")
        
        # Create indexes
        with app.app_context():
            # User indexes
            mongo.db.users.create_index('username', unique=True)
            mongo.db.users.create_index('email', unique=True)
            
            # Workout plan indexes
            mongo.db.workout_plans.create_index([('user_id', 1), ('day_of_week', 1)])
            
            # Diet plan indexes
            mongo.db.diet_plans.create_index([('user_id', 1), ('day_of_week', 1)])
            
            # Tracking indexes
            mongo.db.diet_logs.create_index([('user_id', 1), ('date', 1)])
            mongo.db.workout_logs.create_index([('user_id', 1), ('date', 1)])
            mongo.db.daily_goals.create_index([('user_id', 1), ('date', 1)])
            
            # Meal logs index
            mongo.db.meal_logs.create_index([('user_id', 1), ('created_at', -1)])
            
            # Water logs index
            mongo.db.water_logs.create_index([('user_id', 1), ('created_at', -1)])
            
            # Progress updates index
            mongo.db.progress_updates.create_index([('user_id', 1), ('created_at', -1)])
            
            app.logger.info("MongoDB indexes created successfully")
        
        # Initialize food and exercise databases
        initialize_food_database(mongo)
        initialize_exercise_database(mongo)
        app.logger.info("Food and exercise databases initialized successfully")
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        app.logger.error(f'Error connecting to MongoDB: {str(e)}')
        app.logger.error('Please ensure MongoDB Atlas credentials are correct and the service is accessible')

    # Initialize other extensions
    login.init_app(app)
    login.login_message = 'Please log in to access this page.'
    mail.init_app(app)
    
    # Import models
    from app.models.user import User
    
    @login.user_loader
    def load_user(user_id):
        try:
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            return User(user_data) if user_data else None
        except Exception as e:
            app.logger.error(f"Error loading user: {str(e)}")
            return None
    
    # Import and register blueprints
    from app.routes import main, auth, diet, workout, community, tracking
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(diet.bp)
    app.register_blueprint(workout.bp)
    app.register_blueprint(community.bp)
    app.register_blueprint(tracking.bp)
    
    # Start scheduler if not already running
    if not scheduler.running:
        scheduler.start()
    
    # Add health check endpoint
    @app.route('/health')
    def health_check():
        try:
            mongo.db.command('ping')
            return {'status': 'healthy', 'database': 'connected'}
        except Exception as e:
            return {'status': 'unhealthy', 'database': str(e)}, 500
    
    return app

# Import models after db is defined
from app.models.user import User

@login.user_loader
def load_user(user_id):
    try:
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        return User(user_data) if user_data else None
    except Exception as e:
        app.logger.error(f"Error loading user: {str(e)}")
        return None 