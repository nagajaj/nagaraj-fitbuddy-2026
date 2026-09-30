from typing import Literal
from pydantic import BaseModel, Field, field_validator

Intensity = Literal["low", "medium", "high"]


class UserInput(BaseModel):
    user_id: int = Field(ge=1)
    username: str = Field(min_length=1, max_length=120)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=500)
    goal: str = Field(min_length=3, max_length=500)
    intensity: Intensity

    @field_validator("username", "goal")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty")
        return value


class FeedbackRequest(BaseModel):
    feedback: str = Field(min_length=3, max_length=2000)

    @field_validator("feedback")
    @classmethod
    def clean_feedback(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Feedback cannot be empty")
        return value


class WorkoutRequest(BaseModel):
    goal: str = Field(min_length=3, max_length=500)
    intensity: Intensity


class NutritionTipResponse(BaseModel):
    goal: str
    nutrition_tip: str
