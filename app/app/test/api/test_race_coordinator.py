import pytest
from fastapi.encoders import jsonable_encoder

from app.models.race import RaceStatus, RaceReadDetailCoordinator, RaceReadListCoordinator
from app.models.race_participation import RaceParticipationStatus


def test_coordinator_list_races(coordinator_client, db, race_pending, race_ended):
    response = coordinator_client.get("/api/coordinator/race")
    assert response.status_code == 200
    assert response.json()[-2:] == [
        jsonable_encoder(RaceReadListCoordinator.from_orm(item, update={"is_approved": is_approved})) for
        item, is_approved in
        zip((race_pending, race_ended), (False, True))
    ]


def test_coordinator_race_detail(coordinator_client, db, race_pending):
    response = coordinator_client.get(f"/api/coordinator/race/{race_pending.id}")
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(RaceReadDetailCoordinator.from_orm(race_pending,
                                                                                  update={"is_approved": False}))


def test_coordinator_race_detail_404(coordinator_client, db):
    response = coordinator_client.get("/api/coordinator/race/54654246")
    assert response.status_code == 404


def test_coordinator_create_race(coordinator_client, db, season_1,
                                 disable_celery_tasks):
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
                                           "sponsor_banners_uuids_json": "[]"
                                       })

    assert response.status_code == 200


def test_coordinator_create_race_timestamp_order(coordinator_client, db, season_1,
                                                 disable_celery_tasks):
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
                                           "sponsor_banners_uuids_json": "[]]"
                                       })

    assert response.status_code == 400


def test_coordinator_create_race_zero_laps(coordinator_client, db, season_1,
                                           disable_celery_tasks):
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
                                           "sponsor_banners_uuids_json": "[]"
                                       })

    assert response.status_code == 400


def test_coordinator_create_race_negative_entry_fee(coordinator_client, db, season_1,
                                                    disable_celery_tasks):
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
                                           "sponsor_banners_uuids_json": "[]"
                                       })

    assert response.status_code == 400


def test_coordinator_create_race_invalid_score_json(coordinator_client, db, season_1,
                                                    disable_celery_tasks):
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
                                           "sponsor_banners_uuids_json": "[]"
                                       })

    assert response.status_code == 400


def test_coordinator_create_race_invalid_sponsors_json(coordinator_client, db, season_1, disable_celery_tasks):
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
                                           "sponsor_banners_uuids_json": "[1]"
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


def test_coordinator_update_race(coordinator_client, db, race_pending,
                                 disable_celery_tasks):
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
def test_coordinator_update_race_invalid_status_400(coordinator_client, db, race,
                                                    disable_celery_tasks):
    json = {
        "name": "Different name"
    }
    response = coordinator_client.patch(f"/api/coordinator/race/{race.id}",
                                        json=json)
    assert response.status_code == 400


@pytest.mark.parametrize("race", [
    pytest.lazy_fixture("race_in_progress"),
    pytest.lazy_fixture("race_ended"),
    pytest.lazy_fixture("race_cancelled")
])
def test_coordinator_update_race_weather_conditions_200(coordinator_client, db, race,
                                                        disable_celery_tasks):
    json = {
        "temperature": "cold",
        "rain": "heavy",
        "wind": "zero"
    }
    response = coordinator_client.patch(f"/api/coordinator/race/{race.id}",
                                        json=json)
    assert response.status_code == 200
    assert response.json()['temperature'] == "cold"
    assert response.json()['rain'] == "heavy"
    assert response.json()['wind'] == "zero"


def test_coordinator_update_race_404(coordinator_client, db,
                                     disable_celery_tasks):
    json = {
        "name": "Different name"
    }
    response = coordinator_client.patch("/api/coordinator/race/4536456",
                                        json=json)
    assert response.status_code == 404


def test_race_assign_places(
        race_ended_with_rider_and_multiple_participations, db, coordinator_client,
        disable_celery_tasks
):
    race, participations, riders, bikes = race_ended_with_rider_and_multiple_participations

    places = [2, 1, 4, 3]
    id_to_place_mapping = {p.id: place for p, place in zip(participations, places)}
    json = [
        {
            'id': id,
            'place_assigned_overall': place
        } for id, place in id_to_place_mapping.items()
    ]

    response = coordinator_client.patch(f"/api/coordinator/race/{race.id}/participations",
                                        json=json)

    assert response.status_code == 200
    assert all([p.get("place_assigned_overall") == id_to_place_mapping[p.get('id')] for p in response.json()])
    db.refresh(race)
    assert all([p.place_assigned_overall == id_to_place_mapping[p.id] for p in race.race_participations if
                p.status == RaceParticipationStatus.approved])


def test_race_assign_places_not_all_entries(
        race_ended_with_rider_and_multiple_participations, db, coordinator_client,
        disable_celery_tasks
):
    race, participations, riders, bikes = race_ended_with_rider_and_multiple_participations

    places = [2, 1, 4, 3]
    id_to_place_mapping = {p.id: place for p, place in zip(participations, places)}
    json = [
        {
            'id': id,
            'place_assigned_overall': place
        } for id, place in id_to_place_mapping.items()
    ]
    json.pop()

    response = coordinator_client.patch(f"/api/coordinator/race/{race.id}/participations",
                                        json=json)

    assert response.status_code == 400


def test_race_assign_places_duplicate_entries(
        race_ended_with_rider_and_multiple_participations, db, coordinator_client,
        disable_celery_tasks
):
    race, participations, riders, bikes = race_ended_with_rider_and_multiple_participations

    places = [2, 1, 4, 3]
    id_to_place_mapping = {p.id: place for p, place in zip(participations, places)}
    json = [
               {
                   'id': id,
                   'place_assigned_overall': place
               } for id, place in id_to_place_mapping.items()
           ] + [{'id': participations[0].id, 'place_assigned_overall': 3}]

    response = coordinator_client.patch(f"/api/coordinator/race/{race.id}/participations",
                                        json=json)

    assert response.status_code == 400


@pytest.mark.parametrize('status', [RaceStatus.pending, RaceStatus.cancelled, RaceStatus.in_progress])
def test_race_assign_places_race_not_ended(
        race_ended_with_rider_and_multiple_participations, db, coordinator_client, status,
        disable_celery_tasks
):
    race, participations, riders, bikes = race_ended_with_rider_and_multiple_participations

    race.status = status
    db.add(race)
    db.commit()
    db.refresh(race)

    places = [2, 1, 4, 3]
    id_to_place_mapping = {p.id: place for p, place in zip(participations, places)}
    json = [
               {
                   'id': id,
                   'place_assigned_overall': place
               } for id, place in id_to_place_mapping.items()
           ] + [{'id': participations[0].id, 'place_assigned_overall': 3}]

    response = coordinator_client.patch(f"/api/coordinator/race/{race.id}/participations",
                                        json=json)

    assert response.status_code == 400


@pytest.mark.parametrize('status', [RaceParticipationStatus.pending, RaceParticipationStatus.rejected])
def test_race_assign_places_skip_unapproved(
        race_ended_with_rider_and_multiple_participations, db, coordinator_client, status,
        disable_celery_tasks
):
    race, participations, riders, bikes = race_ended_with_rider_and_multiple_participations

    participations[2].status = status
    db.add(participations[2])
    db.commit()
    db.refresh(participations[2])

    places = [2, 1, 4, 3]
    id_to_place_mapping = {p.id: place for p, place in zip(participations, places)}
    json = [
        {
            'id': id,
            'place_assigned_overall': place
        } for id, place in id_to_place_mapping.items()
    ]

    response = coordinator_client.patch(f"/api/coordinator/race/{race.id}/participations",
                                        json=json)
    assert response.status_code == 200

    assert len(response.json()) == 3
    assert all([p.get("place_assigned_overall") == id_to_place_mapping[p.get('id')] for p in response.json()])
    db.refresh(race)
    db.refresh(participations[2])
    assert all([p.place_assigned_overall == id_to_place_mapping[p.id] for p in race.race_participations if
                p.status == RaceParticipationStatus.approved])
    assert participations[2].place_assigned_overall is None
