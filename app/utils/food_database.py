"""Food database with common measurements and nutritional values"""

def get_common_foods():
    return [
        {
            'name': 'Roti',
            'serving_size': 30,  # in grams
            'calories': 85,
            'protein': 3.0,
            'carbs': 18.0,
            'fats': 0.4,
            'weight_per_piece': 30,
            'weight_per_plate': 90  # assuming 3 rotis
        },
        {
            'name': 'Rice',
            'serving_size': 100,  # in grams
            'calories': 130,
            'protein': 2.7,
            'carbs': 28.0,
            'fats': 0.3,
            'weight_per_bowl': 150,
            'weight_per_cup': 200,
            'weight_per_tbsp': 15
        },
        {
            'name': 'Dal',
            'serving_size': 100,  # in grams
            'calories': 120,
            'protein': 9.0,
            'carbs': 20.0,
            'fats': 1.5,
            'weight_per_bowl': 200,
            'weight_per_cup': 240,
            'weight_per_tbsp': 15
        },
        {
            'name': 'Paneer',
            'serving_size': 100,  # in grams
            'calories': 265,
            'protein': 18.3,
            'carbs': 3.4,
            'fats': 20.8,
            'weight_per_piece': 25,
            'weight_per_cup': 110,
            'weight_per_tbsp': 15
        },
        {
            'name': 'Chicken Curry',
            'serving_size': 100,  # in grams
            'calories': 165,
            'protein': 19.0,
            'carbs': 6.0,
            'fats': 8.0,
            'weight_per_bowl': 200,
            'weight_per_piece': 50  # one piece of chicken
        },
        {
            'name': 'Vegetable Curry',
            'serving_size': 100,  # in grams
            'calories': 85,
            'protein': 2.5,
            'carbs': 10.0,
            'fats': 4.0,
            'weight_per_bowl': 200,
            'weight_per_cup': 240,
            'weight_per_tbsp': 15
        },
        {
            'name': 'Curd',
            'serving_size': 100,  # in grams
            'calories': 98,
            'protein': 11.0,
            'carbs': 3.4,
            'fats': 4.5,
            'weight_per_bowl': 200,
            'weight_per_cup': 245,
            'weight_per_tbsp': 15
        },
        {
            'name': 'Milk',
            'serving_size': 100,  # in ml
            'calories': 67,
            'protein': 3.3,
            'carbs': 4.8,
            'fats': 4.0,
            'weight_per_cup': 240,
            'weight_per_tbsp': 15
        },
        {
            'name': 'Egg',
            'serving_size': 50,  # in grams
            'calories': 78,
            'protein': 6.3,
            'carbs': 0.6,
            'fats': 5.3,
            'weight_per_piece': 50
        },
        {
            'name': 'Bread',
            'serving_size': 30,  # in grams
            'calories': 79,
            'protein': 2.7,
            'carbs': 14.3,
            'fats': 1.0,
            'weight_per_piece': 30,
            'weight_per_slice': 30
        },
        {
            'name': 'Idli',
            'serving_size': 30,  # in grams
            'calories': 39,
            'protein': 2.0,
            'carbs': 8.0,
            'fats': 0.1,
            'weight_per_piece': 30,
            'weight_per_plate': 120  # assuming 4 idlis
        },
        {
            'name': 'Dosa',
            'serving_size': 100,  # in grams
            'calories': 133,
            'protein': 3.8,
            'carbs': 26.0,
            'fats': 1.4,
            'weight_per_piece': 100,
            'weight_per_plate': 100
        }
    ]

def initialize_food_database(mongo):
    """Initialize the food database with common foods"""
    # Drop existing collection
    mongo.db.food_database.drop()
    
    # Insert common foods
    mongo.db.food_database.insert_many(get_common_foods())
    
    # Create index on name
    mongo.db.food_database.create_index([('name', 'text')]) 