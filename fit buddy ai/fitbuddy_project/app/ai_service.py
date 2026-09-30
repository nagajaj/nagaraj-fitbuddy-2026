from functools import lru_cache
from .config import get_settings


def _mock_workout(goal: str, intensity: str) -> str:
    multiplier = {"low": "2 sets", "medium": "3 sets", "high": "3–4 sets"}[intensity]
    days = [
        ("Day 1", "Full Body Strength", ["Squats", "Push-ups", "Bent-over rows"]),
        ("Day 2", "Cardio + Core", ["Brisk walk/jog", "Dead bug", "Plank"]),
        ("Day 3", "Upper Body", ["Incline push-ups", "Dumbbell rows", "Shoulder press"]),
        ("Day 4", "Recovery + Mobility", ["Easy walk", "Hip mobility", "Chest/shoulder mobility"]),
        ("Day 5", "Lower Body", ["Reverse lunges", "Glute bridges", "Calf raises"]),
        ("Day 6", "Cardio + Core", ["Cycling/walking intervals", "Bird dog", "Side plank"]),
        ("Day 7", "Full Body + Stretch", ["Bodyweight squat", "Wall push-ups", "Light rows"]),
    ]
    lines = [f"7-Day FitBuddy Plan — Goal: {goal} — Intensity: {intensity.title()}", ""]
    for day, focus, exercises in days:
        lines += [day + f": {focus}", "Warm-up: 5–10 minutes of easy movement and dynamic mobility.", "Main workout:"]
        for exercise in exercises:
            lines.append(f"- {exercise}: {multiplier}, 8–12 reps (or 30–45 seconds), rest 60–90 seconds.")
        lines += ["Cooldown: 5–10 minutes of easy movement and comfortable stretching.", ""]
    lines += ["Important notes:", "- Increase difficulty gradually and prioritize controlled form.", "- Rest or reduce intensity if you experience unusual pain or excessive fatigue.", "- Hydrate and eat balanced meals that support your goal."]
    return "\n".join(lines)


def _mock_tip(goal: str) -> str:
    return f"For {goal}, prioritize regular hydration, balanced meals, adequate protein, and enough sleep to support training and recovery. Adjust portions and food choices to your individual needs."


@lru_cache
def _client():
    from google import genai
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    return genai.Client(api_key=settings.gemini_api_key)


def _live_text(model: str, prompt: str) -> str:
    from google.genai import types
    response = _client().models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=5000),
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty response")
    return text


def generate_workout(goal: str, intensity: str, age: int | None = None, weight: float | None = None) -> str:
    settings = get_settings()
    if settings.mock_ai and not settings.gemini_api_key:
        return _mock_workout(goal, intensity)
    prompt = f"""You are a professional fitness trainer assistant. Create a practical 7-day workout plan.
User goal: {goal}
Preferred intensity: {intensity}
Age: {age if age is not None else 'not provided'}
Weight (kg): {weight if weight is not None else 'not provided'}

Requirements:
- Clearly label Day 1 through Day 7.
- Every day must include a 5–10 minute warm-up, main workout with exercise details and sets/reps or duration, and a cooldown/recovery tip.
- Adapt exercise selection and volume to the requested intensity and goal.
- Include at least one recovery-oriented day.
- Do not diagnose conditions or prescribe treatment.
- Keep instructions practical and easy to scan.
- Finish with concise safety/progression notes.
"""
    return _live_text(settings.gemini_workout_model, prompt)


def generate_nutrition_tip(goal: str) -> str:
    settings = get_settings()
    if settings.mock_ai and not settings.gemini_api_key:
        return _mock_tip(goal)
    prompt = f"""Give one concise, practical nutrition or recovery tip for someone whose fitness goal is: {goal}.
Keep it to 2–4 sentences. Avoid medical claims, rigid calorie prescriptions, and unsafe dieting advice. Mention hydration, protein, balanced food choices, or recovery when relevant."""
    return _live_text(settings.gemini_flash_model, prompt)


def update_workout(original_plan: str, feedback: str) -> str:
    settings = get_settings()
    if settings.mock_ai and not settings.gemini_api_key:
        return original_plan + f"\n\nFeedback applied in demo mode: {feedback}\n\nRevision note: In live Gemini mode, the plan is regenerated while preserving unaffected sections."
    prompt = f"""You are a professional fitness trainer assistant.

Original 7-day workout plan:
{original_plan}

User feedback:
{feedback}

Revise the plan to address the feedback. Keep the 7-day structure and unaffected content as stable as practical. Return only the revised plan. Avoid medical diagnosis or treatment claims and include sensible rest/safety guidance."""
    return _live_text(settings.gemini_workout_model, prompt)
