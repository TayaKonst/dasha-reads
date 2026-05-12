import uuid
from typing import Any

from pydantic import BaseModel, field_validator


class SessionStartRequest(BaseModel):
    level: int

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: int) -> int:
        if v not in (0, 1, 2, 3):
            raise ValueError("level must be 0, 1, 2, or 3")
        return v


class SessionStartResponse(BaseModel):
    session_id: uuid.UUID


class AnswerRequest(BaseModel):
    exercise_id: uuid.UUID
    answer: str
    response_time_ms: int


class AnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str


class ExerciseOut(BaseModel):
    id: uuid.UUID
    level: int
    type: str
    question_data: dict[str, Any]
    options: list[Any]

    model_config = {"from_attributes": True}


class WeakSpotItem(BaseModel):
    exercise_id: uuid.UUID
    question_data: dict[str, Any]
    correct_answer: str
    level: int
    type: str
    error_rate: float
    attempt_count: int


class StatsSummaryResponse(BaseModel):
    total_sessions: int
    total_attempts: int
    overall_accuracy: float
    sessions_last_7_days: list[str]
