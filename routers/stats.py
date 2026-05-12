from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import Float, case, cast, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Attempt, Exercise, Session
from schemas import StatsSummaryResponse, WeakSpotItem

router = APIRouter()


@router.get("/stats/weak-spots", response_model=list[WeakSpotItem])
async def get_weak_spots(db: AsyncSession = Depends(get_db)):
    error_expr = (
        cast(func.sum(case((Attempt.is_correct == False, 1), else_=0)), Float)  # noqa: E712
        / func.count()
    )

    # Step 1: aggregate by exercise_id only (avoids GROUP BY on JSON column)
    stats_stmt = (
        select(
            Attempt.exercise_id,
            func.count().label("attempt_count"),
            error_expr.label("error_rate"),
        )
        .group_by(Attempt.exercise_id)
        .having(func.count() >= 3, error_expr > 0.4)
    )
    stats_rows = (await db.execute(stats_stmt)).all()

    if not stats_rows:
        return []

    # Step 2: fetch exercise details for matched ids
    ids = [r.exercise_id for r in stats_rows]
    ex_rows = (await db.execute(select(Exercise).where(Exercise.id.in_(ids)))).scalars().all()
    ex_map = {ex.id: ex for ex in ex_rows}

    # Step 3: combine, sort by level then error_rate desc
    combined = sorted(
        stats_rows,
        key=lambda r: (ex_map[r.exercise_id].level, -r.error_rate),
    )

    return [
        WeakSpotItem(
            exercise_id=r.exercise_id,
            question_data=ex_map[r.exercise_id].question_data,
            correct_answer=ex_map[r.exercise_id].correct_answer,
            level=ex_map[r.exercise_id].level,
            type=ex_map[r.exercise_id].type,
            error_rate=r.error_rate,
            attempt_count=r.attempt_count,
        )
        for r in combined
    ]


@router.get("/stats/summary", response_model=StatsSummaryResponse)
async def get_summary(db: AsyncSession = Depends(get_db)):
    total_sessions = (await db.execute(select(func.count()).select_from(Session))).scalar() or 0
    total_attempts = (await db.execute(select(func.count()).select_from(Attempt))).scalar() or 0

    overall_accuracy = (
        await db.execute(select(func.avg(Session.score)).where(Session.score.is_not(None)))
    ).scalar() or 0.0

    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    days_rows = (
        await db.execute(
            select(func.date(Session.started_at).label("day"))
            .where(Session.started_at >= seven_days_ago)
            .group_by(func.date(Session.started_at))
        )
    ).all()
    sessions_last_7_days = [str(r.day) for r in days_rows]

    return StatsSummaryResponse(
        total_sessions=total_sessions,
        total_attempts=total_attempts,
        overall_accuracy=round(float(overall_accuracy), 1),
        sessions_last_7_days=sessions_last_7_days,
    )
