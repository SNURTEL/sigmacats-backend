from typing import Optional
from datetime import datetime

from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from app.core.celery import celery_app
from app.db.session import get_db
from app.models.race import Race, RaceStatus
from app.models.race_participation import RaceParticipation, RaceParticipationStatus
from app.util.log import get_logger

logger = get_logger()


@celery_app.task()
def end_race_and_generate_places(
    race_id: int,
    db: Optional[Session] = None
) -> None:
    if not db:
        db = next(get_db())

    logger.info(f"Assigning places for race {race_id}")
    race = db.get(Race, race_id)

    if not race:
        raise ValueError(f"Race {race_id} not found")

    race.status = RaceStatus.ended

    stmt: SelectOfScalar = (
        select(RaceParticipation)
        .where(
            RaceParticipation.race_id == race.id,
            RaceParticipation.status == RaceParticipationStatus.approved
        )
    )
    participations = db.exec(stmt).all()

    now = datetime.now()

    for p in participations:
        if not p.ride_end_timestamp:
            p.ride_end_timestamp = now
            db.add(p)

    db.commit()
    db.refresh(race)

    prev_timestamp = None
    prev_place = 1
    for i, p in enumerate(sorted(participations, key=lambda p: p.ride_end_timestamp), start=1):
        if p.ride_end_timestamp == prev_timestamp:
            p.place_generated_overall = prev_place
        else:
            p.place_generated_overall = i
        db.add(p)
        prev_timestamp = p.ride_end_timestamp
        prev_place = p.place_generated_overall

    db.add(race)
    db.commit()

    logger.info("Task done!")
