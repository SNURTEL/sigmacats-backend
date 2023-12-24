from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from app.core.users import current_rider_user
from app.db.session import get_db
from app.models.race import Race, RaceReadListRider, RaceReadDetailRider, RaceStatus
from app.models.bike import Bike
from app.models.rider import Rider
from app.models.race_participation import RaceParticipation, RaceParticipationStatus, RaceParticipationCreated

router = APIRouter()


# mypy: disable-error-code=var-annotated

@router.get("/")
async def read_races(
        rider: Rider = Depends(current_rider_user),
        db: Session = Depends(get_db), limit: int = 30, offset: int = 0
) -> list[RaceReadListRider]:
    """
    List all races.
    """
    stmt = (
        select(Race)
        .offset(offset)
        .limit(limit)
        .order_by(Race.start_timestamp.desc())  # type: ignore[arg-type, attr-defined]
    )
    races = db.exec(stmt).all()

    return [RaceReadListRider.from_orm(r, update={
        'participation_status': getattr(
            next((p for p in r.race_participations if p.rider_id == rider.id), None),
            'status', None)
    }) for r in races]


@router.get("/{id}")
async def read_race(
        id: int,
        rider: Rider = Depends(current_rider_user),
        db: Session = Depends(get_db),
) -> RaceReadDetailRider:
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

    return RaceReadDetailRider.from_orm(race, update={
        'participation_status': getattr(
            next((p for p in race.race_participations if p.rider_id == rider.id), None),
            'status', None)
    })


@router.post("/{id}/join")
async def join_race(
        id: int,
        bike_id: int,
        rider: Rider = Depends(current_rider_user),
        db: Session = Depends(get_db),
) -> RaceParticipationCreated:
    """
    Create a race participation.
    """
    stmt = (
        select(Race)
        .where(Race.id == id)
    )
    race = db.exec(stmt).first()
    bike = db.get(Bike, bike_id)

    if not race or not bike or not rider:
        raise HTTPException(404)

    if bike.is_retired:
        raise HTTPException(403, "Cannot join race on a retired bike")

    if race.status != RaceStatus.pending:
        raise HTTPException(403, f"Race already {race.status.name}")

    ongoing_participation = db.exec(select(RaceParticipation).where(
        RaceParticipation.race == race and RaceParticipation.rider == rider)).first()
    if ongoing_participation and ongoing_participation.bike_id == bike_id:
        return RaceParticipationCreated.from_orm(ongoing_participation)

    participation = RaceParticipation(
        race=race,
        status=RaceParticipationStatus.pending,
        rider=rider,
        bike=bike
    )

    db.add(participation)
    db.commit()
    db.refresh(participation)

    return RaceParticipationCreated.from_orm(participation)


@router.post("/{id}/withdraw")
async def withdraw_race(
        id: int,
        rider: Rider = Depends(current_rider_user),
        db: Session = Depends(get_db),
) -> None:
    """
    Withdraw from a race (delete race participation).
    """
    stmt: SelectOfScalar = (
        select(Race)
        .where(Race.id == id)
    )
    race = db.exec(stmt).first()
    db_rider = db.get(Rider, rider.id)
    participation = db.exec(
        select(RaceParticipation).where(RaceParticipation.race == race, RaceParticipation.rider == db_rider)).first()

    if not race or not db_rider:
        raise HTTPException(404)

    if race.status in (RaceStatus.cancelled, RaceStatus.ended):
        raise HTTPException(403, f"Race already {race.status.name}")

    if not participation:
        return

    db.delete(participation)
    db.refresh(race)
    db.commit()

    return
