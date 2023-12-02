from random import randint

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from sqlalchemy.exc import IntegrityError

from app.db.session import get_db

from app.models.race import Race, RaceStatus, RaceCreate, RaceUpdate

router = APIRouter()


@router.get("/")
async def read_races(
        db: Session = Depends(get_db), limit: int = 30, offset: int = 0
) -> list[Race]:
    stmt = (
        select(Race)
        .offset(offset)
        .limit(limit)
        .order_by(Race.id)
    )
    races = db.exec(stmt).all()

    return races


@router.get("/{id}")
async def read_race(
        id: int, db: Session = Depends(get_db),
) -> Race:
    stmt = (
        select(Race)
        .where(Race.id == id)
    )
    race = db.exec(stmt).first()

    if not race:
        raise HTTPException(404)

    return race


@router.put("/create")
async def create_race(
        race_create: RaceCreate,
        db: Session = Depends(get_db),
) -> Race:
    if db.exec(select(Race).where(Race.name == RaceCreate.name, Race.season_id == RaceCreate.season_id)).first():
        raise HTTPException(400, "Race with given name already exists in current season")

    race = Race.from_orm(race_create, update={
        "status": RaceStatus.pending,
        "checkpoints_gpx_file": f"NOT_IMPLEMENTED{randint(0, 9999999999)}",
        "event_graphic_file": f"NOT_IMPLEMENTED{randint(0, 9999999999)}"
    })

    try:
        db.add(race)
        db.commit()
    except IntegrityError:
        raise HTTPException(400)

    return race


@router.patch("/{id}")
async def update_race(
        id: int,
        race_update: RaceUpdate,
        db: Session = Depends(get_db)
) -> Race:
    race = db.get(Race, id)
    if not race:
        raise HTTPException(404)
    race_data = race_update.dict(exclude_unset=True, exclude_defaults=True)
    for k, v in race_data.items():
        setattr(race, k, v)

    db.add(race)
    db.commit()
    db.refresh(race)
    return race


@router.patch("/{id}/cancel")
async def cancel_race(
        id: int,
        db: Session = Depends(get_db)
) -> Race:
    race = db.get(Race, id)
    if not race:
        raise HTTPException(404)
    if race.status == RaceStatus.ended:
        raise HTTPException(400, "Cannot cancel a race which has ended")
    race.status = RaceStatus.cancelled
    db.add(race)
    db.commit()
    db.refresh(race)
    return race
