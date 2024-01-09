import shutil
import uuid
import imghdr
import gpxo
import numpy as np

from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.datastructures import FormData

from sqlmodel import Session, select
from pydantic import ValidationError

from sqlalchemy.exc import IntegrityError

from app.db.session import get_db

from app.models.race import Race, RaceStatus, RaceCreate, RaceUpdate, RaceReadDetailCoordinator, RaceReadListCoordinator
from app.models.season import Season
from app.models.race_participation import RaceParticipationListRead, RaceParticipation, RaceParticipationStatus

LOOP_DISTANCE_THRESHOLD = 0.00015


router = APIRouter()


# mypy: disable-error-code=var-annotated


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
        .order_by(Race.start_timestamp.desc())  # type: ignore[arg-type, attr-defined]
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
        })
        db.add(race)
        db.commit()
    except (IntegrityError, ValidationError):
        raise HTTPException(400)

    return RaceReadDetailCoordinator.from_orm(race)


@router.post("/create/upload-route/", status_code=201)
async def create_upload_route(request: Request) -> dict[str, str]:
    form: FormData = await request.form()
    tmp_path = str(form.get('fileobj.path'))

    with open(tmp_path, 'r') as f:
        content = f.read(43)
        if content.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<gpx'):
            print('GPX')
        else:
            print('INVALID TYPE')
            raise HTTPException(400)

    track = gpxo.Track(tmp_path)
    start_point = track.data.head(1)[['latitude (°)', 'longitude (°)']].values.T.squeeze()
    end_point = track.data.tail(1)[['latitude (°)', 'longitude (°)']].values.T.squeeze()

    # assert track is a loop
    assert np.linalg.norm(start_point - end_point) <= LOOP_DISTANCE_THRESHOLD

    new_name = f"{str(uuid.uuid4())}.gpx"
    new_path = f'/attachments/{new_name}'
    shutil.move(tmp_path, new_path)

    return {  # type: ignore[return-value]
        k: form.get(k) for k in (  # type: ignore[misc]
            'fileobj.content_type',
            'fileobj.md5',
            'fileobj.size',
            'name')
    } | {
        'fileobj.name': new_name,
        'fileobj.path': new_path
    }


@router.post("/create/upload-graphic/", status_code=201)
async def create_upload_graphic(request: Request) -> dict[str, str]:
    form: FormData = await request.form()
    tmp_path = str(form.get('fileobj.path'))

    extension = imghdr.what(tmp_path)
    if extension in ('jpeg', 'png'):
        print(extension)
    else:
        print('INVALID TYPE')
        raise HTTPException(400)

    new_name = f"{str(uuid.uuid4())}.{extension}"
    new_path = f'/attachments/{new_name}'
    shutil.move(tmp_path, new_path)

    return {  # type: ignore[return-value]
        k: form.get(k) for k in (  # type: ignore[misc]
            'fileobj.content_type',
            'fileobj.md5',
            'fileobj.size',
            'name')
    } | {
        'fileobj.name': new_name,
        'fileobj.path': new_path
    }


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
    if race.status != RaceStatus.pending:
        raise HTTPException(400, "Can only edit pending races")
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


@router.get("/{id}/participations")
async def race_list_participants(
        id: int,
        limit: int = 30, offset: int = 0,
        db: Session = Depends(get_db)
) -> list[RaceParticipationListRead]:
    """
    List all participations (no matter what state) in given race.
    """
    race = db.get(Race, id)

    if not race:
        raise HTTPException(404)

    stmt = (
        select(RaceParticipation)
        .where(RaceParticipation.race_id == id)
        .offset(offset)
        .limit(limit) # type: ignore[arg-type, attr-defined]
    )
    participations = db.exec(stmt).all()

    return participations  # type: ignore[return-value]


@router.patch("/{race_id}/participations/{participation_id}/set-status")
async def race_list_participants(
        race_id: int,
        participation_id: int,
        status: RaceParticipationStatus,
        db: Session = Depends(get_db)
) -> RaceParticipationListRead:  # todo create a separate model for that
    """
    Set status of a given race participation
    """
    participation = db.get(RaceParticipation, participation_id)

    if not participation or participation.race_id != race_id:
        raise HTTPException(404)

    participation.status = status
    db.add(participation)
    db.commit()
    db.refresh(participation)

    return participation  # type: ignore[return-value]