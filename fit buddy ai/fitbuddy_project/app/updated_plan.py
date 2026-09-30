from .ai_service import update_workout


def update_workout_plan(original_plan: str, user_feedback: str) -> str:
    """Revise an existing workout plan according to user feedback."""
    return update_workout(original_plan, user_feedback)
