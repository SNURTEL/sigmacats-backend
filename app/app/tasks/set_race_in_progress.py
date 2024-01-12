from typing import Optional

from sqlmodel import Session

from app.core.celery import celery_app
from app.db.session import get_db
from app.util.log import get_logger
from app.models.race import Race, RaceStatus

logger = get_logger()


@celery_app.task()
def set_race_in_progress(race_id: int, db: Optional[Session] = None) -> None:
    logger.info("Scheduled task DONE")

    if not db:
        db = next(get_db())

    race = db.get(Race, race_id)

    if not race:
        logger.error("Clould not find race")
        raise ValueError("Could not find race")

    if race.status != RaceStatus.pending:
        logger.error(f"Race status must be pending (is {race.status.value})")
        raise ValueError(f"Race status must be pending (is {race.status.value})")

    race.status = RaceStatus.in_progress
    db.add(race)
    db.commit()
    db.refresh(race)
