from fastapi.encoders import jsonable_encoder

from app.models.race import RaceReadListRider, RaceStatus, RaceReadDetailCoordinator, RaceReadListCoordinator, \
    RaceReadDetailRider
from app.models.race_participation import RaceParticipationStatus


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
                                      "place_to_points_mapping_json": '[{"place": 1,"points": 20}, {"place": 2,"points": 16}]',
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
                                           "place_to_points_mapping_json": '[{"place": 1,"points": 20}, {"place": 2,"points": 16}]',
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
                                           "place_to_points_mapping_json": '[{"place": 1,"points": 20}, {"place": 2,"points": 16}]',
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
                                           "place_to_points_mapping_json": '[{"place": 1,"points": 20}, {"place": 2,"points": 16}]',
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
                                           "place_to_points_mapping_json": '[{"place": 1,"points": 20}, {"place": 2,"points": 16}]',
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
                                           "place_to_points_mapping_json": '[{"place": 1,"points": 20}, {"place": 2,"points": 16}]',
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
