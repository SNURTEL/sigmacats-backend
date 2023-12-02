from fastapi.encoders import jsonable_encoder

from app.models.race import RaceReadListRider


def test_rider_list_races(client, db, race_pending, race_ended):
    response = client.get("/api/rider/race")
    assert response.status_code == 200
    assert response.json()[-2:] == [jsonable_encoder(RaceReadListRider.from_orm(item)) for item in
                                    (race_pending, race_ended)]
