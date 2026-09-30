from .ai_service import generate_nutrition_tip


def generate_nutrition_tip_with_flash(goal: str) -> str:
    """Generate a concise nutrition/recovery tip using the configured Flash model."""
    return generate_nutrition_tip(goal)
