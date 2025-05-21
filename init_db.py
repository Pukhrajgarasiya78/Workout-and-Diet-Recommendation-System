from app import create_app, db
from app.models import User, DietPlan, WorkoutPlan, MealLog, WorkoutLog, WaterLog, ProgressUpdate
import os

def init_db():
    app = create_app()
    
    with app.app_context():
        try:
            # Drop existing tables if they exist
            try:
                db.drop_all()
                print("Dropped existing tables")
            except Exception as e:
                print(f"Note: Could not drop tables (this is normal for first run): {e}")
            
            # Create new tables
            db.create_all()
            print("Created new tables")
            
            # Create a test user
            test_user = User(
                username='test_user',
                email='test@example.com'
            )
            test_user.set_password('password123')
            
            # Add the test user to the database
            db.session.add(test_user)
            db.session.commit()
            
            print("\nDatabase initialized successfully!")
            print("Test user created:")
            print(f"Username: test_user")
            print(f"Password: password123")
            
        except Exception as e:
            print(f"\nError initializing database: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    init_db() 