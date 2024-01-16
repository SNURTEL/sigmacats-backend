from fastapi.encoders import jsonable_encoder

from app.models.race import RaceReadListRider, RaceReadDetailRider
from app.models.race_participation import RaceParticipationStatus

"""
This files contains tests related to a rider and his race participation
"""


def test_rider_list_races(rider1_client, db, race_pending, race_ended):
    """
    Test listing of races
    """
    response = rider1_client.get("/api/rider/race")
    assert response.status_code == 200
    assert response.json()[-2:] == [jsonable_encoder(RaceReadListRider.from_orm(item)) for item in
                                    (race_pending, race_ended)]


def test_rider_race_detail(rider1_client, db, race_pending):
    """
    Test displaying of race details
    """
    response = rider1_client.get(f"/api/rider/race/{race_pending.id}")
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(RaceReadDetailRider.from_orm(race_pending))


def test_rider_race_detail_404(rider1_client, db, rider1):
    """
    Test displaying of race details of a non-existent race
    """
    response = rider1_client.get("/api/rider/race/54654246")
    assert response.status_code == 404


def test_rider_race_join(rider1_client, db, race_pending, rider1, bike_rider1_road):
    """
    Test joining a race by a rider
    """
    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/join",
                                  params={
                                      "bike_id": bike_rider1_road.id
                                  })
    assert response.status_code == 200
    assert response.json()["status"] == RaceParticipationStatus.pending.value
    assert response.json()["rider_id"] == rider1.id
    assert response.json()["bike_id"] == bike_rider1_road.id
    assert response.json()["race_id"] == race_pending.id


def test_rider_race_status_after_join(rider1_client, db, race_pending, rider1, bike_rider1_road):
    """
    Test status of a race after rider has joined it
    """
    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/join",
                                  params={
                                      "bike_id": bike_rider1_road.id
                                  })
    assert response.status_code == 200

    response = rider1_client.get("/api/rider/race")
    assert response.status_code == 200
    assert response.json()[-1].get('participation_status') == RaceParticipationStatus.pending.value


def test_rider_race_participant_after_join(rider1_client, db, race_pending, rider1, bike_rider1_road):
    """
    Test if rider becomes a race participant after joining a race
    """
    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/join",
                                  params={
                                      "bike_id": bike_rider1_road.id
                                  })
    assert response.status_code == 200

    response = rider1_client.get(f"/api/rider/race/{response.json().get('race_id')}")
    assert response.status_code == 200
    assert any(p.get('rider_id') == rider1.id for p in response.json().get('race_participations'))


def test_rider_race_detail_status_after_join(rider1_client, db, race_pending, rider1, bike_rider1_road):
    """
    Test rider status in race details after rider joined a race
    """
    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/join",
                                  params={
                                      "bike_id": bike_rider1_road.id
                                  })
    assert response.status_code == 200

    response = rider1_client.get(f"/api/rider/race/{response.json().get('race_id')}")
    assert response.status_code == 200
    assert response.json().get("participation_status") == RaceParticipationStatus.pending.value


def test_rider_race_join_multiple(rider1_client, db, race_pending, rider1, bike_rider1_road):
    """
    Test joining multiple races
    """
    ids = set()
    for _ in range(5):
        response = rider1_client.post(f"/api/rider/race/{race_pending.id}/join",
                                      params={
                                          "bike_id": bike_rider1_road.id
                                      })
        assert response.status_code == 200
        ids.add(response.json()["id"])

    assert len(ids) == 1


def test_rider_race_rejoin_different_bike(rider1_client, db, race_pending, rider1, bike_rider1_road, bike_rider1_fixie):
    """
    Test rejoining a race with different bike
    """
    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/join",
                                  params={
                                      "bike_id": bike_rider1_road.id
                                  })
    assert response.status_code == 200
    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/join",
                                  params={
                                      "bike_id": bike_rider1_fixie.id
                                  })
    assert response.status_code == 200

    assert response.json().get('bike_id') == bike_rider1_fixie.id


def test_rider_race_join_ended_403(rider1_client, db, race_ended, rider1, bike_rider1_road):
    """
    Test joining to a finished race
    """
    response = rider1_client.post(f"/api/rider/race/{race_ended.id}/join",
                                  params={
                                      "bike_id": bike_rider1_road.id
                                  })
    assert response.status_code == 403


def test_rider_race_join_bike_404(rider1_client, db, race_pending, rider1, bike_rider1_road):
    """
    Test joining with a non-existent bike
    """
    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/join",
                                  params={
                                      "bike_id": 56474567456
                                  })
    assert response.status_code == 404


def test_rider_race_join_race_404(rider1_client, db, rider1, bike_rider1_road):
    """
    Test joining to a non-existent race
    """
    response = rider1_client.post("/api/rider/race/345673753674/join",
                                  params={
                                      "bike_id": bike_rider1_road.id
                                  })
    assert response.status_code == 404


def test_rider_race_join_bike_retired_403(rider1_client, db, race_pending, rider1, bike_rider1_road):
    """
    Test joining a race with a retired bike
    """
    bike_rider1_road.is_retired = True
    db.add(bike_rider1_road)
    db.commit()
    db.refresh(bike_rider1_road)
    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/join",
                                  params={
                                      "bike_id": bike_rider1_road.id
                                  })
    assert response.status_code == 403


def test_rider_race_withdraw(rider1_client, db, race_pending, rider1, bike_rider1_road):
    """
    Test race withdrawal mechanism
    """
    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/join",
                                  params={
                                      "bike_id": bike_rider1_road.id
                                  })
    assert response.status_code == 200
    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/withdraw")
    assert response.status_code == 200


def test_rider_race_withdraw_multiple(rider1_client, db, race_pending, rider1, bike_rider1_road):
    """
    Test withdrawal mechanism for multiple races
    """
    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/join",
                                  params={"bike_id": bike_rider1_road.id
                                          })
    assert response.status_code == 200

    for _ in range(5):
        response = rider1_client.post(f"/api/rider/race/{race_pending.id}/withdraw", )
        assert response.status_code == 200


def test_rider_race_status_after_withdraw(rider1_client, db, race_pending, rider1, bike_rider1_road):
    """
    Test if race status for a rider is correct after withdrawal
    """
    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/join",
                                  params={
                                      "bike_id": bike_rider1_road.id
                                  })
    assert response.status_code == 200

    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/withdraw")
    assert response.status_code == 200

    response = rider1_client.get("/api/rider/race", params={"rider_id": rider1.id})
    assert response.status_code == 200
    assert response.json()[-1].get('participation_status') is None


def test_rider_race_participant_after_withdraw(rider1_client, db, race_pending, rider1, bike_rider1_road):
    """
    Test if race participant status for a rider is correct after withdrawal
    """
    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/join",
                                  params={
                                      'bike_id': bike_rider1_road.id
                                  })
    assert response.status_code == 200
    race_id = response.json().get('race_id')

    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/withdraw", )
    assert response.status_code == 200

    response = rider1_client.get(f"/api/rider/race/{race_id}", params={"rider_id": rider1.id})
    assert response.status_code == 200
    assert not any(p.get('rider_id') == rider1.id for p in response.json().get('race_participations') if p)


def test_rider_race_detail_status_withdraw(rider1_client, db, race_pending, rider1, bike_rider1_road):
    """
    Test status of race details for a rider after withdrawal
    """
    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/join",
                                  params={
                                      "bike_id": bike_rider1_road.id
                                  })
    assert response.status_code == 200
    race_id = response.json().get('race_id')

    response = rider1_client.post(f"/api/rider/race/{race_pending.id}/withdraw",
                                  params={
                                      "rider_id": rider1.id,
                                  })
    assert response.status_code == 200

    response = rider1_client.get(f"/api/rider/race/{race_id}")
    assert response.status_code == 200
    assert response.json().get('participation_status') is None


def test_rider_race_withdraw_race_ended(rider1_client, db, race_ended, rider1):
    """
    Test withdrawal from a finished race
    """
    response = rider1_client.post(f"/api/rider/race/{race_ended.id}/withdraw", )
    assert response.status_code == 403


def test_rider_race_withdraw_race_404(rider1_client, db, rider1):
    """
    Test withdrawal from a non-existent race
    """
    response = rider1_client.post("/api/rider/race/475645/withdraw", )
    assert response.status_code == 404
