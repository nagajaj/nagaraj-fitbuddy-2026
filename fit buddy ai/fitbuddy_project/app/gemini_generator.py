from .ai_service import generate_workout


def generate_workout_gemini(user_input: dict) -> str:
    """Generate a personalized 7-day plan using the configured Gemini workout model."""
    return generate_workout(user_input["goal"], user_input["intensity"], user_input.get("age"), user_input.get("weight"))
