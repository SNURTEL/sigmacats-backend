from datetime import datetime, timedelta

import pytest
from fastapi.encoders import jsonable_encoder
from sqlmodel import select

from app.tasks.assign_places_in_classifications import assign_places_in_classifications
from app.models.race_participation import RaceParticipation, RaceParticipationStatus
from app.models.ride_participation_classification_place import RiderParticipationClassificationPlace
from app.models.classification import Classification
from app.models.bike import BikeType
from app.models.account import Gender


def test_assign_classification_places_general(
        race_ended, riders_with_bikes, race_participations_factory, classifications, db
):
    (r1, r2, r3, r4), (b1, b2, b3, b4) = riders_with_bikes
    places = [3, 1, 4, 2]

    participations = race_participations_factory(
        race=race_ended,
        riders=(r1, r2, r3, r4),
        bikes=(b1, b2, b3, b4),
        statuses=[RaceParticipationStatus.approved for _ in range(4)],
        entry_kwargs=[{'place_assigned_overall': p} for p in places]
    )

    assign_places_in_classifications(race_id=race_ended.id, db=db)


    entries = db.exec(
        select(RiderParticipationClassificationPlace).where(
            RiderParticipationClassificationPlace.race_participation_id.in_([p.id for p in participations]),
            RiderParticipationClassificationPlace.classification == classifications['general']
        )
    ).all()

    assert len(entries) == 4
    assert all([e.place == place_expected for e, place_expected in zip(entries, places)])


def test_assign_classification_places_road(
        race_ended, riders_with_bikes, race_participations_factory, classifications, db
):
    (r1, r2, r3, r4), (b1, b2, b3, b4) = riders_with_bikes
    places = [3, 1, 4, 2]
    classification_places = [3, 1, 2]

    b3.type = BikeType.fixie
    db.add(b3)
    db.commit()

    participations = race_participations_factory(
        race=race_ended,
        riders=(r1, r2, r3, r4),
        bikes=(b1, b2, b3, b4),
        statuses=[RaceParticipationStatus.approved for _ in range(4)],
        entry_kwargs=[{'place_assigned_overall': p} for p in places]
    )

    assign_places_in_classifications(race_id=race_ended.id, db=db)


    entries = db.exec(
        select(RiderParticipationClassificationPlace).where(
            RiderParticipationClassificationPlace.race_participation_id.in_([p.id for p in participations]),
            RiderParticipationClassificationPlace.classification == classifications['road']
        )
    ).all()

    assert len(entries) == 3
    assert all([e.place == place_expected for e, place_expected in zip(entries, classification_places)])


def test_assign_classification_places_fixie(
        race_ended, riders_with_bikes, race_participations_factory, classifications, db
):
    (r1, r2, r3, r4), (b1, b2, b3, b4) = riders_with_bikes
    places = [3, 1, 4, 2]
    classification_places = [2, 1, 3]

    b1.type = BikeType.fixie
    b2.type = BikeType.fixie
    b3.type = BikeType.fixie
    b4.type = BikeType.road
    db.add_all([b1, b2, b3, b4])
    db.commit()

    participations = race_participations_factory(
        race=race_ended,
        riders=(r1, r2, r3, r4),
        bikes=(b1, b2, b3, b4),
        statuses=[RaceParticipationStatus.approved for _ in range(4)],
        entry_kwargs=[{'place_assigned_overall': p} for p in places]
    )

    assign_places_in_classifications(race_id=race_ended.id, db=db)


    entries = db.exec(
        select(RiderParticipationClassificationPlace).where(
            RiderParticipationClassificationPlace.race_participation_id.in_([p.id for p in participations]),
            RiderParticipationClassificationPlace.classification == classifications['fixie']
        )
    ).all()

    assert len(entries) == 3
    assert all([e.place == place_expected for e, place_expected in zip(entries, classification_places)])


def test_assign_classification_places_men(
        race_ended, riders_with_bikes, race_participations_factory, classifications, db
):
    (r1, r2, r3, r4), (b1, b2, b3, b4) = riders_with_bikes
    places = [3, 1, 4, 2]
    classification_places = [1, 2]

    r1.account.gender = Gender.male
    r2.account.gender = None
    r3.account.gender = Gender.male
    r4.account.gender = None
    db.add_all([r1, r2, r3, r4])
    db.commit()

    participations = race_participations_factory(
        race=race_ended,
        riders=(r1, r2, r3, r4),
        bikes=(b1, b2, b3, b4),
        statuses=[RaceParticipationStatus.approved for _ in range(4)],
        entry_kwargs=[{'place_assigned_overall': p} for p in places]
    )

    assign_places_in_classifications(race_id=race_ended.id, db=db)


    entries = db.exec(
        select(RiderParticipationClassificationPlace).where(
            RiderParticipationClassificationPlace.race_participation_id.in_([p.id for p in participations]),
            RiderParticipationClassificationPlace.classification == classifications['men']
        )
    ).all()

    assert len(entries) == 2
    assert all([e.place == place_expected for e, place_expected in zip(entries, classification_places)])


def test_assign_classification_places_women(
        race_ended, riders_with_bikes, race_participations_factory, classifications, db
):
    (r1, r2, r3, r4), (b1, b2, b3, b4) = riders_with_bikes
    places = [3, 1, 4, 2]
    classification_places = [1, 2]

    r1.account.gender = None
    r2.account.gender = Gender.female
    r3.account.gender = None
    r4.account.gender = Gender.female
    db.add_all([r1, r2, r3, r4])
    db.commit()

    participations = race_participations_factory(
        race=race_ended,
        riders=(r1, r2, r3, r4),
        bikes=(b1, b2, b3, b4),
        statuses=[RaceParticipationStatus.approved for _ in range(4)],
        entry_kwargs=[{'place_assigned_overall': p} for p in places]
    )

    assign_places_in_classifications(race_id=race_ended.id, db=db)


    entries = db.exec(
        select(RiderParticipationClassificationPlace).where(
            RiderParticipationClassificationPlace.race_participation_id.in_([p.id for p in participations]),
            RiderParticipationClassificationPlace.classification == classifications['women']
        )
    ).all()

    assert len(entries) == 2
    assert all([e.place == place_expected for e, place_expected in zip(entries, classification_places)])


@pytest.mark.parametrize("status", [RaceParticipationStatus.pending, RaceParticipationStatus.rejected])
def test_assign_classification_places_skip_unapproved(
        race_ended, riders_with_bikes, race_participations_factory, classifications, db, status
):
    (r1, r2, r3, r4), (b1, b2, b3, b4) = riders_with_bikes
    places = [3, 1, 4, 2]
    classification_places = [3, 1, 2]

    participations = race_participations_factory(
        race=race_ended,
        riders=(r1, r2, r3, r4),
        bikes=(b1, b2, b3, b4),
        statuses=[RaceParticipationStatus.approved, RaceParticipationStatus.approved, status, RaceParticipationStatus.approved],
        entry_kwargs=[{'place_assigned_overall': p} for p in places]
    )

    assign_places_in_classifications(race_id=race_ended.id, db=db)


    entries = db.exec(
        select(RiderParticipationClassificationPlace).where(
            RiderParticipationClassificationPlace.race_participation_id.in_([p.id for p in participations]),
            RiderParticipationClassificationPlace.classification == classifications['general']
        )
    ).all()

    assert len(entries) == 3
    assert all([e.place == place_expected for e, place_expected in zip(entries, classification_places)])