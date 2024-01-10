from datetime import datetime, timedelta

import pytest
from fastapi.encoders import jsonable_encoder

from app.tasks.assign_race_places import end_race_and_assign_places
from app.models.race import RaceStatus, RaceReadDetailCoordinator, RaceReadListCoordinator
from app.models.race_participation import RaceParticipation, RaceParticipationStatus


def test_coordinator_list_races(coordinator_client, db, race_pending, race_ended):
    response = coordinator_client.get("/api/coordinator/race")
    assert response.status_code == 200
    assert response.json()[-2:] == [jsonable_encoder(RaceReadListCoordinator.from_orm(item)) for item in
                                    (race_pending, race_ended)]


def test_coordinator_race_detail(coordinator_client, db, race_pending):
    response = coordinator_client.get(f"/api/coordinator/race/{race_pending.id}")
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(RaceReadDetailCoordinator.from_orm(race_pending))


def test_coordinator_race_detail_404(coordinator_client, db):
    response = coordinator_client.get("/api/coordinator/race/54654246")
    assert response.status_code == 404


def test_coordinator_create_race(coordinator_client, db, season):
    response = coordinator_client.post("/api/coordinator/race/create",
                                       json={
                                           "name": "test",
                                           "description": "test",
                                           "requirements": "test",
                                           "start_timestamp": "2023-12-02T21:48:36.620Z",
                                           "end_timestamp": "2023-12-02T23:48:36.620Z",
                                           "entry_fee_gr": 10000,
                                           "no_laps": 3,
                                           "checkpoints_gpx_file": "/tmp/nginx_upload/0027983891",
                                           "event_graphic_file": "/tmp/nginx_upload/0027983891",
                                           "place_to_points_mapping_json": '[{"place": 1,"points": 20}, '
                                                                           '{"place": 2,"points": 16}]',
                                           "sponsor_banners_uuids_json": "[]",
                                           "season_id": season.id
                                       })

    assert response.status_code == 200


def test_coordinator_create_race_timestamp_order(coordinator_client, db, season):
    response = coordinator_client.post("/api/coordinator/race/create",
                                       json={
                                           "name": "test",
                                           "description": "test",
                                           "requirements": "test",
                                           "start_timestamp": "2023-12-02T23:48:36.620Z",
                                           "end_timestamp": "2023-12-02T21:48:36.620Z",
                                           "entry_fee_gr": 10000,
                                           "no_laps": 3,
                                           "checkpoints_gpx_file": "/tmp/nginx_upload/0027983891",
                                           "event_graphic_file": "/tmp/nginx_upload/0027983891",
                                           "place_to_points_mapping_json": '[{"place": 1,"points": 20}, '
                                                                           '{"place": 2,"points": 16}]',
                                           "sponsor_banners_uuids_json": "[]]",
                                           "season_id": season.id
                                       })

    assert response.status_code == 400


def test_coordinator_create_race_zero_laps(coordinator_client, db, season):
    response = coordinator_client.post("/api/coordinator/race/create",
                                       json={
                                           "name": "test",
                                           "description": "test",
                                           "requirements": "test",
                                           "start_timestamp": "2023-12-02T23:48:36.620Z",
                                           "end_timestamp": "2023-12-02T21:48:36.620Z",
                                           "entry_fee_gr": 10000,
                                           "no_laps": 0,
                                           "checkpoints_gpx_file": "/tmp/nginx_upload/0027983891",
                                           "event_graphic_file": "/tmp/nginx_upload/0027983891",
                                           "place_to_points_mapping_json": '[{"place": 1,"points": 20}, '
                                                                           '{"place": 2,"points": 16}]',
                                           "sponsor_banners_uuids_json": "[]",
                                           "season_id": season.id
                                       })

    assert response.status_code == 400


def test_coordinator_create_race_negative_entry_fee(coordinator_client, db, season):
    response = coordinator_client.post("/api/coordinator/race/create",
                                       json={
                                           "name": "test",
                                           "description": "test",
                                           "requirements": "test",
                                           "start_timestamp": "2023-12-02T23:48:36.620Z",
                                           "end_timestamp": "2023-12-02T21:48:36.620Z",
                                           "entry_fee_gr": -10000,
                                           "no_laps": 1,
                                           "checkpoints_gpx_file": "/tmp/nginx_upload/0027983891",
                                           "event_graphic_file": "/tmp/nginx_upload/0027983891",
                                           "place_to_points_mapping_json": '[{"place": 1,"points": 20}, '
                                                                           '{"place": 2,"points": 16}]',
                                           "sponsor_banners_uuids_json": "[]",
                                           "season_id": season.id
                                       })

    assert response.status_code == 400


def test_coordinator_create_race_season_404(coordinator_client, db, season):
    response = coordinator_client.post("/api/coordinator/race/create",
                                       json={
                                           "name": "test",
                                           "description": "test",
                                           "requirements": "test",
                                           "start_timestamp": "2023-12-02T23:48:36.620Z",
                                           "end_timestamp": "2023-12-02T21:48:36.620Z",
                                           "entry_fee_gr": 10000,
                                           "no_laps": 1,
                                           "checkpoints_gpx_file": "/tmp/nginx_upload/0027983891",
                                           "event_graphic_file": "/tmp/nginx_upload/0027983891",
                                           "place_to_points_mapping_json": '[{"place": 1,"points": 20}, '
                                                                           '{"place": 2,"points": 16}]',
                                           "sponsor_banners_uuids_json": "[]",
                                           "season_id": 45645645
                                       })

    assert response.status_code == 404


def test_coordinator_create_race_invalid_score_json(coordinator_client, db, season):
    response = coordinator_client.post("/api/coordinator/race/create",
                                       json={
                                           "name": "test",
                                           "description": "test",
                                           "requirements": "test",
                                           "start_timestamp": "2023-12-02T21:48:36.620Z",
                                           "end_timestamp": "2023-12-02T23:48:36.620Z",
                                           "entry_fee_gr": 10000,
                                           "no_laps": 3,
                                           "checkpoints_gpx_file": "/tmp/nginx_upload/0027983891",
                                           "event_graphic_file": "/tmp/nginx_upload/0027983891",
                                           "place_to_points_mapping_json": "[{\"place\": 1, \"score\": \"sdfgs\"\"}, "
                                                                           "{\"place\": 2, \"score\": 0\"}]",
                                           "sponsor_banners_uuids_json": "[]",
                                           "season_id": season.id
                                       })

    assert response.status_code == 400


def test_coordinator_create_race_invalid_sponsors_json(coordinator_client, db, season):
    response = coordinator_client.post("/api/coordinator/race/create",
                                       json={
                                           "name": "test",
                                           "description": "test",
                                           "requirements": "test",
                                           "start_timestamp": "2023-12-02T21:48:36.620Z",
                                           "end_timestamp": "2023-12-02T23:48:36.620Z",
                                           "entry_fee_gr": 10000,
                                           "no_laps": 3,
                                           "checkpoints_gpx_file": "/tmp/nginx_upload/0027983891",
                                           "event_graphic_file": "/tmp/nginx_upload/0027983891",
                                           "place_to_points_mapping_json": '[{"place": 1,"points": 20}, '
                                                                           '{"place": 2,"points": 16}]',
                                           "sponsor_banners_uuids_json": "[1]",
                                           "season_id": season.id
                                       })

    assert response.status_code == 400


def test_coordinator_cancel_race(coordinator_client, db, race_pending):
    response = coordinator_client.post(f"/api/coordinator/race/{race_pending.id}/cancel")
    assert response.status_code == 200
    assert response.json()['id'] == race_pending.id
    assert response.json()['status'] == RaceStatus.cancelled.value


def test_coordinator_cancel_race_multiple(coordinator_client, db, race_pending):
    ids = set()
    for _ in range(5):
        response = coordinator_client.post(f"/api/coordinator/race/{race_pending.id}/cancel")
        assert response.status_code == 200
        assert response.json()['status'] == RaceStatus.cancelled.value
        ids.add(response.json()['id'])
    assert len(ids) == 1
    assert ids.pop() == race_pending.id


def test_coordinator_cancel_race_ended(coordinator_client, db, race_ended):
    response = coordinator_client.post(f"/api/coordinator/race/{race_ended.id}/cancel")
    assert response.status_code == 403


def test_coordinator_cancel_race_race_404(coordinator_client, db):
    response = coordinator_client.post("/api/coordinator/race/4545645/cancel")
    assert response.status_code == 404


def test_coordinator_update_race(coordinator_client, db, race_pending):
    json = {
        "name": "Different name"
    }
    response = coordinator_client.patch(f"/api/coordinator/race/{race_pending.id}",
                                        json=json)
    assert response.status_code == 200
    assert response.json()['name'] == "Different name"
    db.refresh(race_pending)
    assert race_pending.name == "Different name"


@pytest.mark.parametrize("race", [
    pytest.lazy_fixture("race_in_progress"),
    pytest.lazy_fixture("race_ended"),
    pytest.lazy_fixture("race_cancelled")
])
def test_coordinator_update_race_invalid_status_400(coordinator_client, db, race):
    json = {
        "name": "Different name"
    }
    response = coordinator_client.patch(f"/api/coordinator/race/{race.id}",
                                        json=json)
    assert response.status_code == 400


def test_coordinator_update_race_404(coordinator_client, db):
    json = {
        "name": "Different name"
    }
    response = coordinator_client.patch("/api/coordinator/race/4536456",
                                        json=json)
    assert response.status_code == 404


def test_race_assign_places(
    race_in_progress_with_rider_and_multiple_participations, db
):
    race, participations, riders, bikes = race_in_progress_with_rider_and_multiple_participations

    now = datetime(2024, 1, 10, 12, 0,0)
    delta = timedelta(seconds=10)
    places = [3, 1, 4, 2]
    for participation, place in zip(participations, places):
        participation.ride_end_timestamp = now + place * delta
        db.add(participation)
    db.commit()

    end_race_and_assign_places(race_id=race.id, db=db)

    for p in participations:
        db.refresh(p)
    db.refresh(race)

    assert all(
        [db.get(RaceParticipation, p.id).place_generated_overall == place for p, place in zip(participations, places)]
    )
    assert race.status == RaceStatus.ended


def test_race_assign_places_identical_time(
    race_in_progress_with_rider_and_multiple_participations, db
):
    race, participations, riders, bikes = race_in_progress_with_rider_and_multiple_participations

    now = datetime(2024, 1, 10, 12, 0,0)
    delta = timedelta(seconds=10)
    places = [2, 1, 4, 2]
    for participation, place in zip(participations, places):
        participation.ride_end_timestamp = now + place * delta
        db.add(participation)
    db.commit()

    end_race_and_assign_places(race_id=race.id, db=db)

    for p in participations:
        db.refresh(p)

    assert all(
        [db.get(RaceParticipation, p.id).place_generated_overall == place for p, place in zip(participations, places)]
    )


def test_race_assign_places_no_end_timestamp(
    race_in_progress_with_rider_and_multiple_participations, db
):
    race, participations, riders, bikes = race_in_progress_with_rider_and_multiple_participations

    now = datetime(2024, 1, 10, 12, 0,0)
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

    end_race_and_assign_places(race_id=race.id, db=db)

    for p in participations:
        db.refresh(p)

    assert all(
        [db.get(RaceParticipation, p.id).place_generated_overall == place for p, place in zip(participations, places)]
    )


@pytest.mark.parametrize("status", [RaceParticipationStatus.pending, RaceParticipationStatus.rejected])
def test_race_assign_places_different_status(
    race_in_progress_with_rider_and_multiple_participations, db, status
):
    race, participations, riders, bikes = race_in_progress_with_rider_and_multiple_participations

    now = datetime(2024, 1, 10, 12, 0,0)
    delta = timedelta(seconds=10)
    places = [3, 1, 4, 2]
    for participation, place in zip(participations, places):
        participation.ride_end_timestamp = now + place * delta
        db.add(participation)
    participations[2].status = status
    db.add(participations[2])
    db.commit()

    end_race_and_assign_places(race_id=race.id, db=db)

    for p in participations:
        db.refresh(p)

    assert participations[0].place_generated_overall == places[0]
    assert participations[1].place_generated_overall == places[1]
    assert participations[2].place_generated_overall == None
    assert participations[3].place_generated_overall == places[3]


def test_race_assign_places_no_participations(
    race_in_progress_with_rider_and_multiple_participations, db
):
    race, participations, riders, bikes = race_in_progress_with_rider_and_multiple_participations

    for p in participations:
        db.delete(p)
    db.commit()
    db.refresh(race)

    # success if nothing thrown
    end_race_and_assign_places(race_id=race.id, db=db)
    assert race.status == RaceStatus.ended



def test_race_assign_places_no_timestamps(
    race_in_progress_with_rider_and_multiple_participations, db
):
    race, participations, riders, bikes = race_in_progress_with_rider_and_multiple_participations

    for participation in participations:
        participation.ride_end_timestamp = None
        db.add(participation)
    db.commit()

    end_race_and_assign_places(race_id=race.id, db=db)

    for p in participations:
        db.refresh(p)
    db.refresh(race)

    assert all(
        [db.get(RaceParticipation, p.id).place_generated_overall == 1 for p in participations]
    )
    assert race.status == RaceStatus.ended


