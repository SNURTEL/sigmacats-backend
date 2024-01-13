from datetime import datetime, timedelta

import pytest

from app.tasks.generate_race_places import end_race_and_generate_places
from app.models.race import RaceStatus
from app.models.race_participation import RaceParticipation, RaceParticipationStatus


def test_race_generate_places(
        race_in_progress_with_rider_and_multiple_participations, db
):
    race, participations, riders, bikes = race_in_progress_with_rider_and_multiple_participations

    now = datetime(2024, 1, 10, 12, 0, 0)
    delta = timedelta(seconds=10)
    places = [3, 1, 4, 2]
    for participation, place in zip(participations, places):
        participation.ride_end_timestamp = now + place * delta
        db.add(participation)
    db.commit()

    end_race_and_generate_places(race_id=race.id, db=db)

    for p in participations:
        db.refresh(p)
    db.refresh(race)

    assert all(
        [db.get(RaceParticipation, p.id).place_generated_overall == place for p, place in zip(participations, places)]
    )
    assert race.status == RaceStatus.ended


def test_race_generate_places_identical_time(
        race_in_progress_with_rider_and_multiple_participations, db
):
    race, participations, riders, bikes = race_in_progress_with_rider_and_multiple_participations

    now = datetime(2024, 1, 10, 12, 0, 0)
    delta = timedelta(seconds=10)
    places = [2, 1, 4, 2]
    for participation, place in zip(participations, places):
        participation.ride_end_timestamp = now + place * delta
        db.add(participation)
    db.commit()

    end_race_and_generate_places(race_id=race.id, db=db)

    for p in participations:
        db.refresh(p)

    assert all(
        [db.get(RaceParticipation, p.id).place_generated_overall == place for p, place in zip(participations, places)]
    )


def test_race_generate_places_no_end_timestamp(
        race_in_progress_with_rider_and_multiple_participations, db
):
    race, participations, riders, bikes = race_in_progress_with_rider_and_multiple_participations

    now = datetime(2024, 1, 10, 12, 0, 0)
    delta = timedelta(seconds=10)
    places = [3, 1, 3, 2]
    for participation, place in zip(participations, places):
        participation.ride_end_timestamp = now + place * delta
        db.add(participation)
    participations[0].ride_end_timestamp = None
    participations[2].ride_end_timestamp = None
    db.add(participations[2])
    db.add(participations[0])
    db.commit()

    end_race_and_generate_places(race_id=race.id, db=db)

    for p in participations:
        db.refresh(p)

    assert all(
        [db.get(RaceParticipation, p.id).place_generated_overall == place for p, place in zip(participations, places)]
    )


@pytest.mark.parametrize("status", [RaceParticipationStatus.pending, RaceParticipationStatus.rejected])
def test_race_generate_places_different_status(
        race_in_progress_with_rider_and_multiple_participations, db, status
):
    race, participations, riders, bikes = race_in_progress_with_rider_and_multiple_participations

    now = datetime(2024, 1, 10, 12, 0, 0)
    delta = timedelta(seconds=10)
    places = [3, 1, 4, 2]
    for participation, place in zip(participations, places):
        participation.ride_end_timestamp = now + place * delta
        db.add(participation)
    participations[2].status = status
    db.add(participations[2])
    db.commit()

    end_race_and_generate_places(race_id=race.id, db=db)

    for p in participations:
        db.refresh(p)

    assert participations[0].place_generated_overall == places[0]
    assert participations[1].place_generated_overall == places[1]
    assert participations[2].place_generated_overall is None
    assert participations[3].place_generated_overall == places[3]


def test_race_generate_places_no_participations(
        race_in_progress_with_rider_and_multiple_participations, db
):
    race, participations, riders, bikes = race_in_progress_with_rider_and_multiple_participations

    for p in participations:
        db.delete(p)
    db.commit()
    db.refresh(race)

    # success if nothing thrown
    end_race_and_generate_places(race_id=race.id, db=db)
    assert race.status == RaceStatus.ended


def test_race_generate_places_no_timestamps(
        race_in_progress_with_rider_and_multiple_participations, db
):
    race, participations, riders, bikes = race_in_progress_with_rider_and_multiple_participations

    for participation in participations:
        participation.ride_end_timestamp = None
        db.add(participation)
    db.commit()

    end_race_and_generate_places(race_id=race.id, db=db)

    for p in participations:
        db.refresh(p)
    db.refresh(race)

    assert all(
        [db.get(RaceParticipation, p.id).place_generated_overall == 1 for p in participations]
    )
    assert race.status == RaceStatus.ended
