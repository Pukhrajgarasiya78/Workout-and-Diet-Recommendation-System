from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Create a minimal Flask application
app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define a simple model
class TestModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

def test_db():
    try:
        # Create tables
        with app.app_context():
            db.create_all()
            print("Successfully created database tables")
            
            # Try to add a test record
            test_record = TestModel(name="test")
            db.session.add(test_record)
            db.session.commit()
            print("Successfully added test record")
            
            # Query the record
            result = TestModel.query.first()
            print(f"Successfully queried test record: {result.name}")
            
            # Clean up
            db.session.delete(result)
            db.session.commit()
            print("Successfully cleaned up test record")
            
            # Drop tables
            db.drop_all()
            print("Successfully dropped database tables")
            
        print("\nAll database operations completed successfully!")
        
    except Exception as e:
        print(f"\nError during database test: {str(e)}")
        raise

if __name__ == '__main__':
    test_db() 