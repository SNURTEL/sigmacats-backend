from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_db

from app.models.race import Race, RaceReadListRider, RaceReadDetailRider, RaceStatus
from app.models.bike import Bike
from app.models.rider import Rider
from app.models.race_participation import RaceParticipation, RaceParticipationStatus, RaceParticipationCreated

router = APIRouter()


@router.get("/")
async def read_races(
        db: Session = Depends(get_db), limit: int = 30, offset: int = 0
) -> list[RaceReadListRider]:
    stmt = (
        select(Race)
        .offset(offset)
        .limit(limit)
        .order_by(Race.id)
    )
    races = db.exec(stmt).all()

    return [RaceReadListRider.from_orm(r) for r in races]


@router.get("/{id}")
async def read_race(
        id: int, db: Session = Depends(get_db),
) -> RaceReadDetailRider:
    stmt = (
        select(Race)
        .where(Race.id == id)
    )
    race = db.exec(stmt).first()

    if not race:
        raise HTTPException(404)

    return RaceReadDetailRider.from_orm(race)


@router.put("/{id}/join")
async def join_race(
        id: int,
        rider_id: int,  # TODO deduce from session
        bike_id: int,
        db: Session = Depends(get_db),
) -> RaceParticipationCreated:
    stmt = (
        select(Race)
        .where(Race.id == id)
    )
    race = db.exec(stmt).first()
    rider = db.get(Rider, rider_id)
    bike = db.get(Bike, bike_id)

    if not race or not bike or not rider:
        raise HTTPException(404)

    if race.status != RaceStatus.pending:
        raise HTTPException(403, f"Race already {race.status.name}")

    ongoing_participation = db.exec(select(RaceParticipation).where(
            RaceParticipation.race == race and RaceParticipation.rider == rider)).first()
    if ongoing_participation:
        return RaceParticipationCreated.from_orm(ongoing_participation)

    participation = RaceParticipation(
        race=race,
        status=RaceParticipationStatus.pending,
        rider=rider,
        bike=bike
    )

    db.add(participation)
    db.commit()

    return RaceParticipationCreated.from_orm(participation)


@router.put("/{id}/withdraw")
async def withdraw_race(
        id: int,
        rider_id: int,  # TODO deduce from session
        db: Session = Depends(get_db),
):
    stmt = (
        select(Race)
        .where(Race.id == id)
    )
    race = db.exec(stmt).first()
    rider = db.get(Rider, rider_id)
    participation = db.exec(
        select(RaceParticipation).where(RaceParticipation.race == race, RaceParticipation.rider == rider)).first()

    if not race or not rider:
        raise HTTPException(404)

    if race.status in (RaceStatus.cancelled, RaceStatus.ended):
        raise HTTPException(403, f"Race already {race.status.name}")

    if not participation:
        return

    db.delete(participation)
    db.commit()

    return
