from app import create_app, db
from app.models import User, DietPlan, WorkoutPlan, MealLog, WorkoutLog

app = create_app()

def view_users():
    with app.app_context():
        users = User.query.all()
        print("\nUsers:")
        print("-" * 50)
        for user in users:
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"First Name: {user.first_name}")
            print(f"Last Name: {user.last_name}")
            print(f"Fitness Goal: {user.fitness_goal}")
            print("-" * 50)

def view_diet_plans():
    with app.app_context():
        plans = DietPlan.query.all()
        print("\nDiet Plans:")
        print("-" * 50)
        for plan in plans:
            print(f"User ID: {plan.user_id}")
            print(f"Day: {plan.day_of_week}")
            print(f"Meal Type: {plan.meal_type}")
            print(f"Plan Data: {plan.plan_data}")
            print("-" * 50)

def view_workout_plans():
    with app.app_context():
        plans = WorkoutPlan.query.all()
        print("\nWorkout Plans:")
        print("-" * 50)
        for plan in plans:
            print(f"User ID: {plan.user_id}")
            print(f"Day: {plan.day_of_week}")
            print(f"Plan Data: {plan.plan_data}")
            print("-" * 50)

if __name__ == "__main__":
    view_users()
    view_diet_plans()
    view_workout_plans() 