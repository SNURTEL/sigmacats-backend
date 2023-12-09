from random import randint

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import ValidationError

from sqlalchemy.exc import IntegrityError

from app.db.session import get_db

from app.models.race import Race, RaceStatus, RaceCreate, RaceUpdate, RaceReadDetailCoordinator, RaceReadListCoordinator
from app.models.season import Season

router = APIRouter()


@router.get("/")
async def read_races(
        db: Session = Depends(get_db), limit: int = 30, offset: int = 0
) -> list[RaceReadListCoordinator]:
    """
    List all races.
    """
    stmt = (
        select(Race)
        .offset(offset)
        .limit(limit)
        .order_by(Race.id)  # type: ignore[arg-type]
    )
    races = db.exec(stmt).all()

    return races  # type: ignore[return-value]


@router.get("/{id}")
async def read_race(
        id: int, db: Session = Depends(get_db),
) -> RaceReadDetailCoordinator:
    """
    Get details about a specific race.
    """
    stmt = (
        select(Race)
        .where(Race.id == id)
    )
    race = db.exec(stmt).first()

    if not race:
        raise HTTPException(404)

    return RaceReadDetailCoordinator.from_orm(race)


@router.post("/create")
async def create_race(
        race_create: RaceCreate,
        db: Session = Depends(get_db),
) -> RaceReadDetailCoordinator:
    """
    Create a new race.
    """
    if db.exec(select(Race).where(Race.name == race_create.name, Race.season_id == race_create.season_id)).first():
        raise HTTPException(400, "Race with given name already exists in current season")

    if not db.get(Season, race_create.season_id):
        raise HTTPException(404)

    try:
        race = Race.from_orm(race_create, update={
            "status": RaceStatus.pending,
            "checkpoints_gpx_file": f"NOT_IMPLEMENTED{randint(0, 9999999999)}",
            "event_graphic_file": f"NOT_IMPLEMENTED{randint(0, 9999999999)}"
        })
        db.add(race)
        db.commit()
    except (IntegrityError, ValidationError):
        raise HTTPException(400)

    return RaceReadDetailCoordinator.from_orm(race)


@router.patch("/{id}")
async def update_race(
        id: int,
        race_update: RaceUpdate,
        db: Session = Depends(get_db)
) -> RaceReadDetailCoordinator:
    """
    Update race details.
    """
    race = db.get(Race, id)
    if not race:
        raise HTTPException(404)
    try:
        race_data = race_update.dict(exclude_unset=True, exclude_defaults=True)
        for k, v in race_data.items():
            setattr(race, k, v)
        db.add(race)
        db.commit()
        db.refresh(race)
    except (IntegrityError, ValidationError):
        raise HTTPException(400)

    return RaceReadDetailCoordinator.from_orm(race)


@router.post("/{id}/cancel")
async def cancel_race(
        id: int,
        db: Session = Depends(get_db)
) -> RaceReadDetailCoordinator:
    """
    Cancel race event.
    """
    race = db.get(Race, id)
    if not race:
        raise HTTPException(404)
    if race.status == RaceStatus.ended:
        raise HTTPException(403, "Cannot cancel a race which has ended")
    race.status = RaceStatus.cancelled
    db.add(race)
    db.commit()
    db.refresh(race)
    return RaceReadDetailCoordinator.from_orm(race)
