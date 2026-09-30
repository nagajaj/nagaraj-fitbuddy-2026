from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import User, WorkoutPlan
from .schemas import UserInput


def save_user(db: Session, user_data: UserInput) -> User:
    user = db.get(User, user_data.user_id)
    if user is None:
        user = User(id=user_data.user_id)
        db.add(user)
    user.name = user_data.username
    user.age = user_data.age
    user.weight = user_data.weight
    user.goal = user_data.goal
    user.intensity = user_data.intensity
    db.flush()
    return user


def save_plan(db: Session, user_id: int, plan: str, nutrition_tip: str | None = None) -> WorkoutPlan:
    workout = db.scalar(select(WorkoutPlan).where(WorkoutPlan.user_id == user_id))
    if workout is None:
        workout = WorkoutPlan(user_id=user_id, original_plan=plan)
        db.add(workout)
    else:
        workout.original_plan = plan
        workout.updated_plan = None
        workout.feedback = None
    workout.nutrition_tip = nutrition_tip
    db.commit()
    db.refresh(workout)
    return workout


def update_plan(db: Session, user_id: int, updated_text: str, feedback: str) -> WorkoutPlan | None:
    workout = db.scalar(select(WorkoutPlan).where(WorkoutPlan.user_id == user_id))
    if workout is None:
        return None
    workout.updated_plan = updated_text
    workout.feedback = feedback
    db.commit()
    db.refresh(workout)
    return workout


def get_original_plan(db: Session, user_id: int) -> str | None:
    workout = db.scalar(select(WorkoutPlan).where(WorkoutPlan.user_id == user_id))
    return workout.original_plan if workout else None


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_all_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.id)).all())
