import shutil
import uuid

import imghdr
import gpxo
import pytz
import numpy as np

from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.datastructures import FormData

from sqlmodel import Session, select
from pydantic import ValidationError

from sqlalchemy.exc import IntegrityError

from app.core.celery import celery_app
from app.db.session import get_db
from app.util.log import get_logger
from app.tasks.set_race_in_progress import set_race_in_progress

from app.tasks.generate_race_places import end_race_and_generate_places
from app.tasks.assign_places_in_classifications import assign_places_in_classifications

from app.models.race import Race, RaceStatus, RaceCreate, RaceUpdate, RaceReadDetailCoordinator, \
    RaceReadListCoordinator, RaceReadUpdatedCoordinator
from app.models.season import Season
from app.models.race_participation import RaceParticipationCoordinatorListRead, RaceParticipation, \
    RaceParticipationStatus, \
    RaceParticipationAssignPlaceListUpdate, RaceParticipationListReadNames

LOOP_DISTANCE_THRESHOLD = 0.00015

router = APIRouter()

logger = get_logger()

"""
This file contains API endpoints related to race management available for race coordinators
"""


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

    return [RaceReadListCoordinator.from_orm(r, update={
        "is_approved": any([p.place_assigned_overall is not None for p in
                            r.race_participations]) or (r.status == RaceStatus.ended and not r.race_participations)})
            for
            r in races]  # type: ignore[return-value]


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

    is_approved = any([p.place_assigned_overall is not None for p in race.race_participations]) or (
            race.status == RaceStatus.ended and not race.race_participations)

    return RaceReadDetailCoordinator.from_orm(race, update={
        "is_approved": is_approved,
        "race_participations": [RaceParticipationListReadNames.from_orm(p, update={
            "rider_name": p.rider.account.name,
            "rider_surname": p.rider.account.surname,
            "rider_username": p.rider.account.username,
            "time_seconds": p.ride_end_timestamp - p.ride_start_timestamp if (
                    p.ride_start_timestamp and p.ride_end_timestamp) else None
        }) for p in race.race_participations]
    })


@router.post("/create")
async def create_race(
        race_create: RaceCreate,
        db: Session = Depends(get_db),
) -> RaceReadDetailCoordinator:
    """
    Create a new race and schedule a Celery task to set status to `in_progress` on race start.
    """
    current_season = db.exec(
        select(Season)
        .order_by(Season.start_timestamp.desc())  # type: ignore[attr-defined]
    ).first()

    if not current_season:
        raise HTTPException(500, "Could not find current season")

    if db.exec(select(Race).where(
            Race.name == race_create.name,
            Race.season_id == current_season.id
    )).first():
        raise HTTPException(400, "Race with given name already exists in current season")

    try:
        race = Race.from_orm(race_create, update={
            "status": RaceStatus.pending,
            "season_id": current_season.id
        })
        db.add(race)
        db.commit()
    except (IntegrityError, ValidationError) as e:
        logger.error("Creating race failed: " + repr(e))
        raise HTTPException(400)

    db.refresh(race)

    tz = pytz.timezone('Poland')
    task_id = set_race_in_progress.apply_async(args=[race.id],
                                               eta=tz.localize(race.start_timestamp).astimezone(pytz.UTC))

    race.celery_task_id = str(task_id)
    db.add(race)
    db.commit()

    return RaceReadDetailCoordinator.from_orm(race, update={"is_approved": False})


@router.post("/create/upload-route/", status_code=201)
async def create_upload_route(request: Request) -> dict[str, str]:
    """
    Upload GPX route for a race. This endpoint is used only for processing requests forwarded by the
    `nginx-upload` module and will not do anything meaningful if called directly.
    """
    form: FormData = await request.form()
    tmp_path = str(form.get('fileobj.path'))

    with open(tmp_path, 'r') as f:
        content = f.read(43)
        if not content.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<gpx'):
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
    """
    Upload graphic for a race. This endpoint is used only for processing requests forwarded by the `nginx-upload`
    module and will not do anything meaningful if called directly.
    """
    form: FormData = await request.form()
    tmp_path = str(form.get('fileobj.path'))

    extension = imghdr.what(tmp_path)
    if extension not in ('jpeg', 'png'):
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
) -> RaceReadUpdatedCoordinator:
    """
    Update race details.
    """
    race = db.get(Race, id)
    if not race:
        raise HTTPException(404)

    if (race.status != RaceStatus.pending
            and not set(race_update.dict(exclude_unset=True, exclude_defaults=True).keys()).issubset(
                {"temperature", "rain", "wind"})):
        raise HTTPException(400, "Can only update temperature, rain and wind in non-pending races")
    try:
        race_data = race_update.dict(exclude_unset=True, exclude_defaults=True)
        for k, v in race_data.items():
            setattr(race, k, v)

        db.add(race)
        db.commit()
        db.refresh(race)

        if race_update.start_timestamp is not None:
            celery_app.control.revoke(race.celery_task_id, terminate=True)
            tz = pytz.timezone('Poland')
            task_id = set_race_in_progress.apply_async(args=[race.id],
                                                       eta=tz.localize(race.start_timestamp).astimezone(pytz.UTC))
            race.celery_task_id = str(task_id)
            db.add(race)
            db.commit()

    except (IntegrityError, ValidationError):
        raise HTTPException(400)

    return RaceReadUpdatedCoordinator.from_orm(race, update={
        "is_approved": any([p.place_assigned_overall is not None for p in race.race_participations]) or (
                race.status == RaceStatus.ended and not race.race_participations)})


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
    return RaceReadDetailCoordinator.from_orm(race, update={"is_approved": False})


@router.get("/{id}/participations")
async def race_list_participants(
        id: int,
        limit: int = 30, offset: int = 0,
        db: Session = Depends(get_db)
) -> list[RaceParticipationCoordinatorListRead]:
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
        .limit(limit)  # type: ignore[arg-type, attr-defined]
    )
    participations = db.exec(stmt).all()

    return participations  # type: ignore[return-value]


@router.patch("/{race_id}/participations/{participation_id}/set-status")
async def race_participation_set_status(
        race_id: int,
        participation_id: int,
        status: RaceParticipationStatus,
        db: Session = Depends(get_db)
) -> RaceParticipationCoordinatorListRead:
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


@router.patch("/{id}/force-end")
async def race_force_end(
        id: int,
        db: Session = Depends(get_db)
) -> list[RaceParticipationCoordinatorListRead]:
    """
    End the race immediately and trigger Celery task
    for assigning places in classifications.
    """
    race = db.get(Race, id)
    if not race:
        raise HTTPException(404)

    end_race_and_generate_places(race_id=id, db=db)

    db.refresh(race)
    return [RaceParticipationCoordinatorListRead.from_orm(r) for r in race.race_participations]


@router.patch("/{id}/participations")
async def race_assign_places(
        id: int,
        race_participation_updates: list[RaceParticipationAssignPlaceListUpdate],
        db: Session = Depends(get_db)
) -> list[RaceParticipationCoordinatorListRead]:
    """
    Manually assign places to race participants
    """
    race = db.get(Race, id)

    if not race:
        raise HTTPException(404)

    if race.status != RaceStatus.ended:
        raise HTTPException(400, "Cannot assign places before race has ended")

    stmt = (
        select(RaceParticipation)
        .where(
            RaceParticipation.race_id == id,
            RaceParticipation.status == RaceParticipationStatus.approved
        )
    )
    participations = db.exec(stmt).all()

    updates_approved = [rpu for rpu in race_participation_updates if rpu.id in {p.id for p in participations}]

    if any([p.place_assigned_overall is not None for p in participations]):
        raise HTTPException(400, "Places already assigned.")

    if (not len(updates_approved) == len(participations)
            or {rpu.id for rpu in updates_approved} != {p.id for p in participations}):
        raise HTTPException(400, "Cannot map provided updates to race participations 1:1")

    if not all([rpu.place_assigned_overall > 0 for rpu in updates_approved]):
        raise HTTPException(400, "Places must be at least 1")

    id_to_participation_mapping = {p.id: p for p in participations}

    for rpu in updates_approved:
        p = id_to_participation_mapping[rpu.id]
        p.place_assigned_overall = rpu.place_assigned_overall
        db.add(p)

    db.commit()
    db.refresh(race)

    assign_places_in_classifications.delay(race_id=id)

    return [RaceParticipationCoordinatorListRead.from_orm(p) for p in race.race_participations if
            p.status == RaceParticipationStatus.approved]
