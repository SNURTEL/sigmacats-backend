import asyncio
from typing import Generator, Any
import contextlib
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import select, Session

from app.core.users import get_user_manager, get_user_db, get_db, current_rider_user, current_active_user, \
    current_coordinator_user, current_admin_user
from app.models.account import Account, AccountCreate, AccountType
from app.models.rider import Rider
from app.models.bike import Bike, BikeType
from app.models.season import Season
from app.models.race import Race, RaceStatus, RaceTemperature, RaceRain
from app.models.race_bonus import RaceBonus

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


    stmt = (
        select(Account)
        .where(Account.type == AccountType.rider)
        .order_by(Account.id.desc())
    )
    rider_account = db.exec(stmt).first()

    yield rider_account.rider


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
def bike_road(db, rider1) -> Generator[Bike, Any, None]:
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
def bike_fixie(db, rider1) -> Generator[Bike, Any, None]:
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


@pytest.fixture(scope="function")
def rider2_client(rider2):
    app.dependency_overrides[current_active_user] = lambda: rider2.account
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def coordinator_client(coordinator):
    app.dependency_overrides[current_active_user] = lambda: coordinator.account
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def admin_client(admin):
    app.dependency_overrides[current_active_user] = lambda: admin.account
    with TestClient(app) as c:
        yield c
