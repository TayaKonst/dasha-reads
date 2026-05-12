from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Exercise
from schemas import ExerciseOut

router = APIRouter()


@router.get("/exercises/{level}", response_model=list[ExerciseOut])
async def get_exercises(level: int, limit: int = 10, db: AsyncSession = Depends(get_db)):
    if level not in (0, 1, 2, 3):
        raise HTTPException(status_code=400, detail="level must be 0, 1, 2, or 3")

    result = await db.execute(
        select(Exercise)
        .where(Exercise.level == level, Exercise.is_active == True)  # noqa: E712
        .order_by(func.random())
        .limit(limit)
    )
    return result.scalars().all()
