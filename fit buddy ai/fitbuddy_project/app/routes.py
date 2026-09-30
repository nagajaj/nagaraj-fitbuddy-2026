from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .crud import get_all_users, get_original_plan, save_plan, save_user, update_plan
from .database import get_db
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .schemas import FeedbackRequest, NutritionTipResponse, UserInput, WorkoutRequest
from .updated_plan import update_workout_plan
from .models import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout_page(
    request: Request,
    user_id: int = Form(...),
    username: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(user_id=user_id, username=username, age=age, weight=weight, goal=goal, intensity=intensity)
        plan = generate_workout_gemini(data.model_dump())
        tip = generate_nutrition_tip_with_flash(data.goal)
        save_user(db, data)
        save_plan(db, data.user_id, plan, tip)
        return templates.TemplateResponse(request=request, name="result.html", context={"user": data, "workout_plan": plan, "nutrition_tip": tip, "updated": False})
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="error.html", context={"error": str(exc)}, status_code=500)


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback_page(
    request: Request,
    user_id: int = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        request_data = FeedbackRequest(feedback=feedback)
        original = get_original_plan(db, user_id)
        if not original:
            return templates.TemplateResponse(request=request, name="error.html", context={"error": "Original plan not found for this user."}, status_code=404)
        updated = update_workout_plan(original, request_data.feedback)
        update_plan(db, user_id, updated, request_data.feedback)
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return templates.TemplateResponse(request=request, name="result.html", context={"user": user, "workout_plan": updated, "nutrition_tip": user.workout_plan.nutrition_tip if user.workout_plan else None, "updated": True})
    except HTTPException:
        raise
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="error.html", context={"error": str(exc)}, status_code=500)


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = get_all_users(db)
    rows = []
    for user in users:
        plan = user.workout_plan
        rows.append({
            "id": user.id,
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "original_plan": plan.original_plan if plan else "N/A",
            "updated_plan": plan.updated_plan if plan and plan.updated_plan else "Not updated",
        })
    return templates.TemplateResponse(request=request, name="all_users.html", context={"users": rows})


@router.post("/generate-workout/gemini")
def generate_gemini_workout(request: WorkoutRequest):
    try:
        result = generate_workout_gemini(request.model_dump())
        return {"model": "gemini-workout", "workout_plan": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/nutrition-tip", response_model=NutritionTipResponse)
def get_flash_tip(goal: str):
    try:
        return NutritionTipResponse(goal=goal, nutrition_tip=generate_nutrition_tip_with_flash(goal))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/generate-plan")
def generate_plan(user_data: UserInput, db: Session = Depends(get_db)):
    try:
        save_user(db, user_data)
        plan = generate_workout_gemini(user_data.model_dump())
        tip = generate_nutrition_tip_with_flash(user_data.goal)
        save_plan(db, user_data.user_id, plan, tip)
        return {"message": "Workout plan generated and saved successfully", "workout_plan": plan, "nutrition_tip": tip}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Something went wrong: {exc}") from exc


@router.post("/update-plan/{user_id}")
def update_user_plan(user_id: int, data: FeedbackRequest, db: Session = Depends(get_db)):
    original = get_original_plan(db, user_id)
    if not original:
        raise HTTPException(status_code=404, detail="Original plan not found for this user.")
    try:
        updated = update_workout_plan(original, data.feedback)
        update_plan(db, user_id, updated, data.feedback)
        return {"updated_plan": updated}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
