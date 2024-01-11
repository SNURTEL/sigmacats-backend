import asyncio
import shutil
import os
from typing import Generator, Any
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import select, Session
from sqlmodel.sql.expression import SelectOfScalar

from app.core.users import get_user_manager, get_user_db, current_active_user
from app.tasks.process_race_result_submission import process_race_result_submission

from app.models.account import Account, AccountCreate, AccountType
from app.models.rider import Rider
from app.models.bike import Bike, BikeType
from app.models.season import Season
from app.models.race import Race, RaceStatus, RaceTemperature, RaceRain
from app.models.race_participation import RaceParticipation, RaceParticipationStatus
from app.models.race_bonus import RaceBonus
from app.models.classification import Classification
from app.models.rider_classification_link import RiderClassificationLink

from app.main import app


async def create_account(
        session: Session,
        account_create: AccountCreate
):
    user_db_generator = get_user_db(session)
    user_manager_generator = get_user_manager(next(user_db_generator))
    user_manager = next(user_manager_generator)
    return await user_manager.create(
        account_create,
        safe=False  # allow to set is_superuser and is_verified
    )


@pytest.fixture(scope="function")
def rider1(db) -> Generator[Rider, Any, None]:
    rider_create = AccountCreate(
        type=AccountType.rider,
        username="balbinka123",
        name="Test",
        surname="Rider",
        email="t.rider1@sigma.org",
        password="qwerty123"
    )

    asyncio.run(create_account(
        db,
        rider_create
    ))

    stmt: SelectOfScalar = (
        select(Account)
        .where(Account.type == AccountType.rider)
        .order_by(Account.id.desc())  # type: ignore[union-attr]
    )
    rider_account = db.exec(stmt).first()

    yield rider_account.rider


@pytest.fixture(scope="function")
def bike_rider2(db, rider2) -> Generator[Bike, Any, None]:
    bike = Bike(
        name="Rakieta2",
        type=BikeType.road,
        brand="Canyon",
        model="Ultimate CFR eTap",
        rider=rider2
    )
    db.add(bike)
    db.commit()
    yield bike


@pytest.fixture(scope="function")
def bike_rider3(db, rider3) -> Generator[Bike, Any, None]:
    bike = Bike(
        name="Rakieta3",
        type=BikeType.road,
        brand="Canyon",
        model="Ultimate CFR eTap",
        rider=rider3
    )
    db.add(bike)
    db.commit()
    yield bike


@pytest.fixture(scope="function")
def bike_rider4(db, rider4) -> Generator[Bike, Any, None]:
    bike = Bike(
        name="Rakieta4",
        type=BikeType.road,
        brand="Canyon",
        model="Ultimate CFR eTap",
        rider=rider4
    )
    db.add(bike)
    db.commit()
    yield bike

@pytest.fixture(scope="function")
def rider2(db) -> Generator[Rider, Any, None]:
    rider_create = AccountCreate(
        type=AccountType.rider,
        username="balbinka456",
        name="Test",
        surname="Rider",
        email="t.rider2@sigma.org",
        password="qwerty123"
    )

    rider_account = asyncio.run(create_account(
        db,
        rider_create
    ))

    yield rider_account.rider


@pytest.fixture(scope="function")
def rider3(db) -> Generator[Rider, Any, None]:
    rider_create = AccountCreate(
        type=AccountType.rider,
        username="balbinka666",
        name="Test",
        surname="Rider",
        email="t.rider3@sigma.org",
        password="qwerty123"
    )

    rider_account = asyncio.run(create_account(
        db,
        rider_create
    ))

    yield rider_account.rider


@pytest.fixture(scope="function")
def rider4(db) -> Generator[Rider, Any, None]:
    rider_create = AccountCreate(
        type=AccountType.rider,
        username="balbinka777",
        name="Test",
        surname="Rider",
        email="t.rider4@sigma.org",
        password="qwerty123"
    )

    rider_account = asyncio.run(create_account(
        db,
        rider_create
    ))

    yield rider_account.rider


@pytest.fixture(scope="function")
def coordinator(db) -> Generator[Rider, Any, None]:
    coordinator_create = AccountCreate(
        type=AccountType.coordinator,
        username="coord",
        name="Test",
        surname="Coordinator",
        email="t.coordinator@sigma.org",
        password="qwerty123",
        phone_number="+48123456789"
    )

    coordinator_account = asyncio.run(create_account(
        db,
        coordinator_create
    ))

    yield coordinator_account.coordinator


@pytest.fixture(scope="function")
def admin(db) -> Generator[Rider, Any, None]:
    admin_create = AccountCreate(
        type=AccountType.admin,
        username="admin",
        name="Test",
        surname="Admin",
        email="t.admin@sigma.org",
        password="qwerty123",
        phone_number="+48123456789"
    )

    admin_account = asyncio.run(create_account(
        db,
        admin_create
    ))

    yield admin_account.admin


@pytest.fixture(scope="function")
def bike_rider1_road(db, rider1) -> Generator[Bike, Any, None]:
    bike = Bike(
        name="Rakieta",
        type=BikeType.road,
        brand="Canyon",
        model="Ultimate CFR eTap",
        rider=rider1
    )
    db.add(bike)
    db.commit()
    yield bike


@pytest.fixture(scope="function")
def bike_rider1_fixie(db, rider1) -> Generator[Bike, Any, None]:
    bike = Bike(
        name="Czarna strzała",
        type=BikeType.fixie,
        brand="FIXIE inc.",
        model="Floater Race",
        rider=rider1
    )
    db.add(bike)
    db.commit()
    yield bike


@pytest.fixture(scope="function")
def season(db) -> Generator[Season, Any, None]:
    season = Season(
        name="Sezon 1",
        start_timestamp=datetime(day=2, month=10, year=2021),
        end_timestamp=datetime(day=19, month=2, year=2024)
    )
    db.add(season)
    db.commit()
    yield season


@pytest.fixture(scope="function")
def race_bonus_snow(db) -> Generator[RaceBonus, Any, None]:
    bonus = RaceBonus(
        name="bonus",
        rule="NOT_IMPLEMENTED",
        points_multiplier=2.0
    )
    db.add(bonus)
    db.commit()
    yield bonus


@pytest.fixture(scope="function")
def race_pending(db, season, race_bonus_snow) -> Generator[Race, Any, None]:
    race = Race(
        status=RaceStatus.pending,
        name="Jazda w śniegu",
        description="Jak w tytule. blablabla",
        checkpoints_gpx_file="foo1",
        meetup_timestamp=datetime(day=20, month=12, year=2022, hour=12),
        start_timestamp=datetime(day=20, month=12, year=2022, hour=12, minute=30),
        end_timestamp=datetime(day=20, month=12, year=2022, hour=14),
        entry_fee_gr=1500,
        no_laps=3,
        temperature=RaceTemperature.cold,
        rain=RaceRain.light,
        event_graphic_file="foo1",
        place_to_points_mapping_json='['
                                     '{"place": 1,"points": 20},'
                                     '{"place": 999,"points": 4}'
                                     ']',
        sponsor_banners_uuids_json='["foo1"]',
        season=season,
        bonuses=[race_bonus_snow],
        race_participations=[]
    )
    db.add(race)
    db.commit()
    yield race


@pytest.fixture(scope="function")
def race_in_progress(db, season, race_bonus_snow) -> Generator[Race, Any, None]:
    race = Race(
        status=RaceStatus.in_progress,
        name="Jazda w śniegu",
        description="Jak w tytule. blablabla",
        checkpoints_gpx_file="foo1",
        meetup_timestamp=datetime(day=20, month=12, year=2022, hour=12),
        start_timestamp=datetime(day=20, month=12, year=2022, hour=12, minute=30),
        end_timestamp=datetime(day=20, month=12, year=2022, hour=14),
        entry_fee_gr=1500,
        no_laps=3,
        temperature=RaceTemperature.cold,
        rain=RaceRain.light,
        event_graphic_file="foo1",
        place_to_points_mapping_json='['
                                     '{"place": 1,"points": 20},'
                                     '{"place": 999,"points": 4}'
                                     ']',
        sponsor_banners_uuids_json='["foo1"]',
        season=season,
        bonuses=[race_bonus_snow],
        race_participations=[]
    )
    db.add(race)
    db.commit()
    yield race


@pytest.fixture(scope="function")
def race_in_progress_with_rider_and_participation(db, race_in_progress, rider1, bike_rider1_road, sample_track_gpx) -> Generator[tuple[Race, RaceParticipation, Rider, Bike], Any, None]:
    race_in_progress.checkpoints_gpx_file = sample_track_gpx

    participation = RaceParticipation(
        status=RaceParticipationStatus.approved,
        rider=rider1,
        bike=bike_rider1_road,
        race=race_in_progress
    )

    db.add(race_in_progress)
    db.add(participation)
    db.commit()
    db.refresh(race_in_progress)

    yield race_in_progress, participation, rider1, bike_rider1_road


@pytest.fixture(scope="function")
def race_in_progress_with_rider_and_multiple_participations(
        db, race_in_progress,
        rider1, rider2, rider3, rider4,
        bike_rider1_road, bike_rider2, bike_rider3, bike_rider4,
        sample_track_gpx) -> Generator[tuple[Race, list[RaceParticipation], list[Rider], list[Bike]], Any, None]:

    race_in_progress.checkpoints_gpx_file = sample_track_gpx

    riders = [rider1, rider2, rider3, rider4]
    bikes = [bike_rider1_road, bike_rider2, bike_rider3, bike_rider4]

    participations = [
        RaceParticipation(
            status=RaceParticipationStatus.approved,
            rider=rider,
            bike=bike,
            race=race_in_progress
        )
    for rider, bike in zip(riders, bikes)]

    for participation in participations:
        db.add(participation)

    db.add(race_in_progress)
    db.commit()
    db.refresh(race_in_progress)

    yield race_in_progress, participations, riders, bikes


@pytest.fixture(scope="function")
def race_ended_with_rider_and_multiple_participations(
        db, race_ended,
        rider1, rider2, rider3, rider4,
        bike_rider1_road, bike_rider2, bike_rider3, bike_rider4,
        sample_track_gpx) -> Generator[tuple[Race, list[RaceParticipation], list[Rider], list[Bike]], Any, None]:

    race_ended.checkpoints_gpx_file = sample_track_gpx

    riders = [rider1, rider2, rider3, rider4]
    bikes = [bike_rider1_road, bike_rider2, bike_rider3, bike_rider4]

    participations = [
        RaceParticipation(
            status=RaceParticipationStatus.approved,
            rider=rider,
            bike=bike,
            race=race_ended,
            place_generated_overall=i
        )
    for i, (rider, bike) in enumerate(zip(riders, bikes), start=1)]

    for participation in participations:
        db.add(participation)

    db.add(race_ended)
    db.commit()
    db.refresh(race_ended)

    yield race_ended, participations, riders, bikes


@pytest.fixture(scope="function")
def race_cancelled(db, season, race_bonus_snow) -> Generator[Race, Any, None]:
    race = Race(
        status=RaceStatus.cancelled,
        name="Jazda w śniegu",
        description="Jak w tytule. blablabla",
        checkpoints_gpx_file="foo1",
        meetup_timestamp=datetime(day=20, month=12, year=2022, hour=12),
        start_timestamp=datetime(day=20, month=12, year=2022, hour=12, minute=30),
        end_timestamp=datetime(day=20, month=12, year=2022, hour=14),
        entry_fee_gr=1500,
        no_laps=3,
        temperature=RaceTemperature.cold,
        rain=RaceRain.light,
        event_graphic_file="foo1",
        place_to_points_mapping_json='['
                                     '{"place": 1,"points": 20},'
                                     '{"place": 999,"points": 4}'
                                     ']',
        sponsor_banners_uuids_json='["foo1"]',
        season=season,
        bonuses=[race_bonus_snow],
        race_participations=[]
    )
    db.add(race)
    db.commit()
    yield race


@pytest.fixture(scope="function")
def race_ended(db, season) -> Generator[Race, Any, None]:
    race = Race(
        status=RaceStatus.ended,
        name="Coffe ride: Pożegnanie lata",
        description="opis.",
        requirements="Kask",
        checkpoints_gpx_file="foo2",
        meetup_timestamp=datetime(day=1, month=10, year=2022, hour=11, minute=30),
        start_timestamp=datetime(day=1, month=10, year=2022, hour=12, minute=00),
        end_timestamp=datetime(day=1, month=10, year=2022, hour=15),
        entry_fee_gr=0,
        no_laps=1,
        event_graphic_file="foo2",
        place_to_points_mapping_json='['
                                     '{"place": 999,"points": 10}'
                                     ']',
        sponsor_banners_uuids_json='["foo2"]',
        season=season,
        bonuses=[],
        race_participations=[]
    )
    db.add(race)
    db.commit()
    yield race


# note: use only one of these at a time

@pytest.fixture(scope="function")
def rider1_client(rider1, db):
    stmt = (
        select(Account)
        .where(Account.type == AccountType.rider, Account.rider == rider1)
        .order_by(Account.id.desc())
    )
    rider_account = db.exec(stmt).first()

    app.dependency_overrides[current_active_user] = lambda: rider_account
    with TestClient(app) as c:
        yield c

    del app.dependency_overrides[current_active_user]


@pytest.fixture(scope="function")
def rider2_client(rider2):
    app.dependency_overrides[current_active_user] = lambda: rider2.account
    with TestClient(app) as c:
        yield c

    del app.dependency_overrides[current_active_user]


@pytest.fixture(scope="function")
def coordinator_client(coordinator):
    app.dependency_overrides[current_active_user] = lambda: coordinator.account
    with TestClient(app) as c:
        yield c

    del app.dependency_overrides[current_active_user]


@pytest.fixture(scope="function")
def admin_client(admin):
    app.dependency_overrides[current_active_user] = lambda: admin.account
    with TestClient(app) as c:
        yield c

    del app.dependency_overrides[current_active_user]


@pytest.fixture(scope="function")
def classification_with_rider(db, season, rider1) -> Generator[Classification, Any, None]:
    classification = Classification(
        name="Dzieci",
        description="<18 lat",
        season=season,
    )

    riderClassificationLink = RiderClassificationLink(  # noqa: F841
        score=10,
        rider=rider1,
        classification=classification
    )

    db.add(classification)
    db.commit()
    yield classification


@pytest.fixture(scope="function")
def classification_without_rider(db, season) -> Generator[Classification, Any, None]:
    classification = Classification(
        name="Dorośli",
        description=">=18 lat",
        season=season,
        riders=[]
    )

    db.add(classification)
    db.commit()
    yield classification


@pytest.fixture(scope="function")
def sample_track_gpx() -> Generator[str, Any, None]:
    asset_path = 'app/test/assets/track.gpx'
    new_path = '/attachments/track.gpx'
    shutil.copy2(asset_path, new_path)

    yield new_path

    try:
        os.remove(new_path)
    except FileNotFoundError:
        pass  # if removed by some other function


@pytest.fixture(scope="function")
def sample_ride_gpx() -> Generator[str, Any, None]:
    asset_path = 'app/test/assets/test_recording.gpx'
    new_path = '/attachments/test_recording.gpx'
    shutil.copy2(asset_path, new_path)

    yield new_path

    try:
        os.remove(new_path)
    except FileNotFoundError:
        pass  # if removed by some other function

@pytest.fixture(scope="function")
def disable_celery_tasks(monkeypatch):
    monkeypatch.setattr(process_race_result_submission, 'delay', lambda *args, **kwargs: None)
