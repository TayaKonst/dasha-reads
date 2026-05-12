import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Attempt, Exercise, Session
from schemas import AnswerRequest, AnswerResponse, SessionStartRequest, SessionStartResponse

router = APIRouter()


@router.post("/sessions/start", response_model=SessionStartResponse)
async def start_session(body: SessionStartRequest, db: AsyncSession = Depends(get_db)):
    session = Session(level=body.level)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return SessionStartResponse(session_id=session.id)


@router.post("/sessions/{session_id}/answer", response_model=AnswerResponse)
async def submit_answer(session_id: uuid.UUID, body: AnswerRequest, db: AsyncSession = Depends(get_db)):
    session_result = await db.execute(select(Session).where(Session.id == session_id))
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    exercise_result = await db.execute(select(Exercise).where(Exercise.id == body.exercise_id))
    exercise = exercise_result.scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    is_correct = body.answer.strip().lower() == exercise.correct_answer.strip().lower()

    attempt = Attempt(
        session_id=session_id,
        exercise_id=body.exercise_id,
        child_answer=body.answer,
        is_correct=is_correct,
        response_time_ms=body.response_time_ms,
    )
    db.add(attempt)

    session.total_questions += 1
    if is_correct:
        session.correct_answers += 1

    await db.commit()
    return AnswerResponse(is_correct=is_correct, correct_answer=exercise.correct_answer)


@router.post("/sessions/{session_id}/complete")
async def complete_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    total = session.total_questions or 0
    session.score = (session.correct_answers / total * 100) if total > 0 else 0.0
    session.completed_at = datetime.now(timezone.utc)

    await db.commit()
    return {
        "score": session.score,
        "total_questions": session.total_questions,
        "correct_answers": session.correct_answers,
    }
