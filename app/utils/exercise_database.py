"""Exercise database with MET values for calorie calculations"""

def get_common_exercises():
    """Returns a list of common exercises with their MET values and descriptions"""
    return [
        {
            'name': 'Walking',
            'met': 3.5,
            'description': 'Regular walking at moderate pace',
            'category': 'Cardio'
        },
        {
            'name': 'Running',
            'met': 8.0,
            'description': 'Running at moderate pace (5-7 mph)',
            'category': 'Cardio'
        },
        {
            'name': 'Cycling',
            'met': 7.0,
            'description': 'Cycling at moderate pace',
            'category': 'Cardio'
        },
        {
            'name': 'Swimming',
            'met': 6.0,
            'description': 'Swimming laps at moderate pace',
            'category': 'Cardio'
        },
        {
            'name': 'Yoga',
            'met': 3.0,
            'description': 'General yoga practice',
            'category': 'Flexibility'
        },
        {
            'name': 'Weight Training',
            'met': 4.0,
            'description': 'General weight/resistance training',
            'category': 'Strength'
        },
        {
            'name': 'Push-ups',
            'met': 3.5,
            'description': 'Body weight push-ups',
            'category': 'Strength'
        },
        {
            'name': 'Squats',
            'met': 3.5,
            'description': 'Body weight squats',
            'category': 'Strength'
        },
        {
            'name': 'Jumping Jacks',
            'met': 8.0,
            'description': 'Vigorous jumping jacks',
            'category': 'Cardio'
        },
        {
            'name': 'Pilates',
            'met': 3.5,
            'description': 'General pilates exercises',
            'category': 'Flexibility'
        },
        {
            'name': 'Dancing',
            'met': 4.5,
            'description': 'General dancing/aerobic dance',
            'category': 'Cardio'
        },
        {
            'name': 'Stretching',
            'met': 2.5,
            'description': 'General stretching exercises',
            'category': 'Flexibility'
        },
        {
            'name': 'Plank',
            'met': 3.0,
            'description': 'Static plank hold',
            'category': 'Strength'
        },
        {
            'name': 'Stair Climbing',
            'met': 4.0,
            'description': 'Climbing stairs',
            'category': 'Cardio'
        }
    ]

def initialize_exercise_database(mongo):
    """Initialize the exercise database with common exercises"""
    try:
        # Drop existing collection
        mongo.db.exercise_database.drop()
        
        # Insert common exercises
        exercises = get_common_exercises()
        mongo.db.exercise_database.insert_many(exercises)
        
        # Create text index on exercise names
        mongo.db.exercise_database.create_index([('name', 'text')])
        
        print("Exercise database initialized successfully")
    except Exception as e:
        print(f"Error initializing exercise database: {str(e)}") 