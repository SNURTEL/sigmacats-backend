from typing import Generator, Any

import pytest

from datetime import datetime

from app.models.account import Account
from app.models.rider import Rider
from app.models.bike import Bike, BikeType
from app.models.season import Season
from app.models.race import Race, RaceStatus, RaceTemperature, RaceRain
from app.models.race_bonus import RaceBonus
from app.models.classification import Classification
from app.models.rider_classification_link import RiderClassificationLink


@pytest.fixture(scope="function")
def rider(db) -> Generator[Rider, Any, None]:
    rider_account = Account(
        type="rider",
        username="balbinka123",
        name="Test",
        surname="Rider",
        email="t.rider@sigma.org",
        password_hash="JSDHFGKIUSDFHBKGSBHDFKGS",
    )

    rider = Rider(
        account=rider_account
    )

    db.add(rider)
    db.commit()
    yield rider


@pytest.fixture(scope="function")
def bike_road(db, rider) -> Generator[Bike, Any, None]:
    bike = Bike(
        name="Rakieta",
        type=BikeType.road,
        brand="Canyon",
        model="Ultimate CFR eTap",
        rider=rider
    )
    db.add(bike)
    db.commit()
    yield bike


@pytest.fixture(scope="function")
def bike_fixie(db, rider) -> Generator[Bike, Any, None]:
    bike = Bike(
        name="Czarna strzała",
        type=BikeType.fixie,
        brand="FIXIE inc.",
        model="Floater Race",
        rider=rider
    )
    db.add(bike)
    db.commit()
    yield bike


@pytest.fixture(scope="function")
def season(db) -> Generator[Season, Any, None]:
    season = Season(
        name="Sezon 1",
        start_timestamp=datetime(day=2, month=10, year=2023),
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
        meetup_timestamp=datetime(day=20, month=12, year=2023, hour=12),
        start_timestamp=datetime(day=20, month=12, year=2023, hour=12, minute=30),
        end_timestamp=datetime(day=20, month=12, year=2023, hour=14),
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
        meetup_timestamp=datetime(day=1, month=10, year=2023, hour=11, minute=30),
        start_timestamp=datetime(day=1, month=10, year=2023, hour=12, minute=00),
        end_timestamp=datetime(day=1, month=10, year=2023, hour=15),
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


@pytest.fixture(scope="function")
def classification_with_rider(db, season, rider) -> Generator[Classification, Any, None]:

    classification = Classification(
        name="Dzieci",
        description="<18 lat",
        season=season,
    )

    riderClassificationLink = RiderClassificationLink(  # noqa: F841
        score=10,
        rider=rider,
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
