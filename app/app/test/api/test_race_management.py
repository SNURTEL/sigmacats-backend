from fastapi.encoders import jsonable_encoder

from app.models.race import RaceReadListRider, Race, RaceStatus, RaceReadDetailCoordinator, RaceReadListCoordinator, \
    RaceReadDetailRider
from app.models.race_participation import RaceParticipationStatus, RaceParticipationListRead


def test_rider_list_races(client, rider, db, race_pending, race_ended):
    response = client.get("/api/rider/race", params={"rider_id": rider.id})
    assert response.status_code == 200
    assert response.json()[-2:] == [jsonable_encoder(RaceReadListRider.from_orm(item)) for item in
                                    (race_pending, race_ended)]


def test_coordinator_list_races(client, db, race_pending, race_ended):
    response = client.get("/api/coordinator/race")
    assert response.status_code == 200
    assert response.json()[-2:] == [jsonable_encoder(RaceReadListCoordinator.from_orm(item)) for item in
                                    (race_pending, race_ended)]


def test_rider_race_detail(client, db, race_pending):
    response = client.get(f"/api/rider/race/{race_pending.id}")
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(RaceReadDetailRider.from_orm(race_pending))


def test_coordinator_race_detail(client, db, race_pending):
    response = client.get(f"/api/coordinator/race/{race_pending.id}")
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(RaceReadDetailCoordinator.from_orm(race_pending))


def test_rider_race_detail_404(client, db):
    response = client.get("/api/rider/race/54654246")
    assert response.status_code == 404


def test_coordinator_race_detail_404(client, db):
    response = client.get("/api/coordinator/race/54654246")
    assert response.status_code == 404


def test_rider_race_join(client, db, race_pending, rider, bike_road):
    response = client.post(f"/api/rider/race/{race_pending.id}/join",
                           params={
                               "rider_id": rider.id,
                               "bike_id": bike_road.id
                           })
    assert response.status_code == 200
    assert response.json()["status"] == RaceParticipationStatus.pending.value
    assert response.json()["rider_id"] == rider.id
    assert response.json()["bike_id"] == bike_road.id
    assert response.json()["race_id"] == race_pending.id


def test_rider_race_status_after_join(client, db, race_pending, rider, bike_road):
    response = client.post(f"/api/rider/race/{race_pending.id}/join",
                           params={
                               "rider_id": rider.id,
                               "bike_id": bike_road.id
                           })
    assert response.status_code == 200

    response = client.get("/api/rider/race", params={"rider_id": rider.id})
    assert response.status_code == 200
    assert response.json()[-1].get('participation_status') == RaceParticipationStatus.pending.value


def test_rider_race_participant_after_join(client, db, race_pending, rider, bike_road):
    response = client.post(f"/api/rider/race/{race_pending.id}/join",
                           params={
                               "rider_id": rider.id,
                               "bike_id": bike_road.id
                           })
    assert response.status_code == 200

    response = client.get(f"/api/rider/race/{response.json().get('race_id')}", params={"rider_id": rider.id})
    assert response.status_code == 200
    assert any(p.get('rider_id') == rider.id for p in response.json().get('race_participations'))


def test_rider_race_join_multiple(client, db, race_pending, rider, bike_road):
    ids = set()
    for _ in range(5):
        response = client.post(f"/api/rider/race/{race_pending.id}/join",
                               params={
                                   "rider_id": rider.id,
                                   "bike_id": bike_road.id
                               })
        assert response.status_code == 200
        ids.add(response.json()["id"])

    assert len(ids) == 1


def test_rider_race_rejoin_different_bike(client, db, race_pending, rider, bike_road, bike_fixie):
    response = client.post(f"/api/rider/race/{race_pending.id}/join",
                           params={
                               "rider_id": rider.id,
                               "bike_id": bike_road.id
                           })
    assert response.status_code == 200
    response = client.post(f"/api/rider/race/{race_pending.id}/join",
                           params={
                               "rider_id": rider.id,
                               "bike_id": bike_fixie.id
                           })
    assert response.status_code == 200

    assert response.json().get('bike_id') == bike_fixie.id


def test_rider_race_join_ended_403(client, db, race_ended, rider, bike_road):
    response = client.post(f"/api/rider/race/{race_ended.id}/join",
                           params={
                               "rider_id": rider.id,
                               "bike_id": bike_road.id
                           })
    assert response.status_code == 403


def test_rider_race_join_rider_404(client, db, race_pending, bike_road):
    response = client.post(f"/api/rider/race/{race_pending.id}/join",
                           params={
                               "rider_id": 34632456345,
                               "bike_id": bike_road.id
                           })
    assert response.status_code == 404


def test_rider_race_join_bike_404(client, db, race_pending, rider, bike_road):
    response = client.post(f"/api/rider/race/{race_pending.id}/join",
                           params={
                               "rider_id": rider.id,
                               "bike_id": 56474567456
                           })
    assert response.status_code == 404


def test_rider_race_join_race_404(client, db, rider, bike_road):
    response = client.post("/api/rider/race/345673753674/join",
                           params={
                               "rider_id": rider.id,
                               "bike_id": bike_road.id
                           })
    assert response.status_code == 404


def test_rider_race_join_bike_retired_403(client, db, race_pending, rider, bike_road):
    bike_road.is_retired = True
    db.add(bike_road)
    db.commit()
    db.refresh(bike_road)
    response = client.post(f"/api/rider/race/{race_pending.id}/join",
                           params={
                               "rider_id": rider.id,
                               "bike_id": bike_road.id
                           })
    assert response.status_code == 403


def test_rider_race_withdraw(client, db, race_pending, rider, bike_road):
    response = client.post(f"/api/rider/race/{race_pending.id}/join",
                           params={
                               "rider_id": rider.id,
                               "bike_id": bike_road.id
                           })
    assert response.status_code == 200
    response = client.post(f"/api/rider/race/{race_pending.id}/withdraw",
                           params={
                               "rider_id": rider.id,
                           })
    assert response.status_code == 200


def test_rider_race_withdraw_multiple(client, db, race_pending, rider, bike_road):
    response = client.post(f"/api/rider/race/{race_pending.id}/join",
                           params={
                               "rider_id": rider.id,
                               "bike_id": bike_road.id
                           })
    assert response.status_code == 200

    for _ in range(5):
        response = client.post(f"/api/rider/race/{race_pending.id}/withdraw",
                               params={
                                   "rider_id": rider.id,
                               })
        assert response.status_code == 200


def test_rider_race_status_after_withdraw(client, db, race_pending, rider, bike_road):
    response = client.post(f"/api/rider/race/{race_pending.id}/join",
                           params={
                               "rider_id": rider.id,
                               "bike_id": bike_road.id
                           })
    assert response.status_code == 200

    response = client.post(f"/api/rider/race/{race_pending.id}/withdraw",
                           params={
                               "rider_id": rider.id,
                           })
    assert response.status_code == 200

    response = client.get("/api/rider/race", params={"rider_id": rider.id})
    assert response.status_code == 200
    assert response.json()[-1].get('participation_status') is None


def test_rider_race_participant_after_withdraw(client, db, race_pending, rider, bike_road):
    response = client.post(f"/api/rider/race/{race_pending.id}/join",
                           params={
                               "rider_id": rider.id,
                               "bike_id": bike_road.id
                           })
    assert response.status_code == 200
    race_id = response.json().get('race_id')

    response = client.post(f"/api/rider/race/{race_pending.id}/withdraw",
                           params={
                               "rider_id": rider.id,
                           })
    assert response.status_code == 200

    response = client.get(f"/api/rider/race/{race_id}", params={"rider_id": rider.id})
    assert response.status_code == 200
    assert not any(p.get('rider_id') == rider.id for p in response.json().get('race_participations') if p)


def test_rider_race_withdraw_race_ended(client, db, race_ended, rider):
    response = client.post(f"/api/rider/race/{race_ended.id}/withdraw",
                           params={
                               "rider_id": rider.id,
                           })
    assert response.status_code == 403


def test_rider_race_withdraw_race_404(client, db, rider):
    response = client.post("/api/rider/race/475645/withdraw",
                           params={
                               "rider_id": rider.id,
                           })
    assert response.status_code == 404


def test_rider_race_withdraw_rider_404(client, db, race_pending, bike_road):
    response = client.post(f"/api/rider/race/{race_pending.id}/join",
                           params={
                               "rider_id": 4567567,
                               "bike_id": bike_road.id
                           })
    assert response.status_code == 404


def test_coordinator_create_race(client, db, season):
    response = client.post("/api/coordinator/race/create",
                           json={
                               "name": "test",
                               "description": "test",
                               "requirements": "test",
                               "start_timestamp": "2023-12-02T21:48:36.620Z",
                               "end_timestamp": "2023-12-02T23:48:36.620Z",
                               "entry_fee_gr": 10000,
                               "no_laps": 3,
                               "place_to_points_mapping_json": '[{"place": 1,"points": 20}, {"place": 2,"points": 16}]',
                               "sponsor_banners_uuids_json": "[]",
                               "season_id": season.id
                           })

    assert response.status_code == 200


def test_coordinator_create_race_timestamp_order(client, db, season):
    response = client.post("/api/coordinator/race/create",
                           json={
                               "name": "test",
                               "description": "test",
                               "requirements": "test",
                               "start_timestamp": "2023-12-02T23:48:36.620Z",
                               "end_timestamp": "2023-12-02T21:48:36.620Z",
                               "entry_fee_gr": 10000,
                               "no_laps": 3,
                               "place_to_points_mapping_json": '[{"place": 1,"points": 20}, {"place": 2,"points": 16}]',
                               "sponsor_banners_uuids_json": "[]]",
                               "season_id": season.id
                           })

    assert response.status_code == 400


def test_coordinator_create_race_zero_laps(client, db, season):
    response = client.post("/api/coordinator/race/create",
                           json={
                               "name": "test",
                               "description": "test",
                               "requirements": "test",
                               "start_timestamp": "2023-12-02T23:48:36.620Z",
                               "end_timestamp": "2023-12-02T21:48:36.620Z",
                               "entry_fee_gr": 10000,
                               "no_laps": 0,
                               "place_to_points_mapping_json": '[{"place": 1,"points": 20}, {"place": 2,"points": 16}]',
                               "sponsor_banners_uuids_json": "[]",
                               "season_id": season.id
                           })

    assert response.status_code == 400


def test_coordinator_create_race_negative_entry_fee(client, db, season):
    response = client.post("/api/coordinator/race/create",
                           json={
                               "name": "test",
                               "description": "test",
                               "requirements": "test",
                               "start_timestamp": "2023-12-02T23:48:36.620Z",
                               "end_timestamp": "2023-12-02T21:48:36.620Z",
                               "entry_fee_gr": -10000,
                               "no_laps": 1,
                               "place_to_points_mapping_json": '[{"place": 1,"points": 20}, {"place": 2,"points": 16}]',
                               "sponsor_banners_uuids_json": "[]",
                               "season_id": season.id
                           })

    assert response.status_code == 400


def test_coordinator_create_race_season_404(client, db, season):
    response = client.post("/api/coordinator/race/create",
                           json={
                               "name": "test",
                               "description": "test",
                               "requirements": "test",
                               "start_timestamp": "2023-12-02T23:48:36.620Z",
                               "end_timestamp": "2023-12-02T21:48:36.620Z",
                               "entry_fee_gr": 10000,
                               "no_laps": 1,
                               "place_to_points_mapping_json": '[{"place": 1,"points": 20}, {"place": 2,"points": 16}]',
                               "sponsor_banners_uuids_json": "[]",
                               "season_id": 45645645
                           })

    assert response.status_code == 404


def test_coordinator_create_race_invalid_score_json(client, db, season):
    response = client.post("/api/coordinator/race/create",
                           json={
                               "name": "test",
                               "description": "test",
                               "requirements": "test",
                               "start_timestamp": "2023-12-02T21:48:36.620Z",
                               "end_timestamp": "2023-12-02T23:48:36.620Z",
                               "entry_fee_gr": 10000,
                               "no_laps": 3,
                               "place_to_points_mapping_json": "[{\"place\": 1, \"score\": \"sdfgs\"\"}, "
                                                               "{\"place\": 2, \"score\": 0\"}]",
                               "sponsor_banners_uuids_json": "[]",
                               "season_id": season.id
                           })

    assert response.status_code == 400


def test_coordinator_create_race_invalid_sponsors_json(client, db, season):
    response = client.post("/api/coordinator/race/create",
                           json={
                               "name": "test",
                               "description": "test",
                               "requirements": "test",
                               "start_timestamp": "2023-12-02T21:48:36.620Z",
                               "end_timestamp": "2023-12-02T23:48:36.620Z",
                               "entry_fee_gr": 10000,
                               "no_laps": 3,
                               "place_to_points_mapping_json": '[{"place": 1,"points": 20}, {"place": 2,"points": 16}]',
                               "sponsor_banners_uuids_json": "[1]",
                               "season_id": season.id
                           })

    assert response.status_code == 400


def test_coordinator_cancel_race(client, db, race_pending):
    response = client.post(f"/api/coordinator/race/{race_pending.id}/cancel")
    assert response.status_code == 200
    assert response.json()['id'] == race_pending.id
    assert response.json()['status'] == RaceStatus.cancelled.value


def test_coordinator_cancel_race_multiple(client, db, race_pending):
    ids = set()
    for _ in range(5):
        response = client.post(f"/api/coordinator/race/{race_pending.id}/cancel")
        assert response.status_code == 200
        assert response.json()['status'] == RaceStatus.cancelled.value
        ids.add(response.json()['id'])
    assert len(ids) == 1
    assert ids.pop() == race_pending.id


def test_coordinator_cancel_race_ended(client, db, race_ended):
    response = client.post(f"/api/coordinator/race/{race_ended.id}/cancel")
    assert response.status_code == 403


def test_coordinator_cancel_race_race_404(client, db):
    response = client.post("/api/coordinator/race/4545645/cancel")
    assert response.status_code == 404
