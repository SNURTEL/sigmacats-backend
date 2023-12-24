from fastapi.encoders import jsonable_encoder

from app.models.bike import Bike, BikeType


def test_read_bikes(rider1_client, rider1, db, bike_road, bike_fixie):
    response = rider1_client.get("/api/rider/bike", params={"rider_id": rider1.id})
    assert response.status_code == 200
    # assert response.json()[-2:] == [jsonable_encoder(Bike.from_orm(item)) for item in
    #                                 (bike_road, bike_fixie)]


def test_read_bike(rider1_client, rider1, db, bike_road, bike_fixie):
    response = rider1_client.get(f"/api/rider/bike/{bike_road.id}", params={"rider_id": rider1.id})
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(bike_road)


def test_read_bike_404(rider1_client, rider1, db, bike_road, bike_fixie):
    response = rider1_client.get("/api/rider/bike/78567856", params={"rider_id": rider1.id})
    assert response.status_code == 404


def test_create_bike(rider1_client, rider1, db):
    json = {
        "name": "Amazon Special",
        "type": BikeType.road.value,
        "brand": "Eurobike",
        "model": "XC550 Road Bike,21 Speed Bikes for Women and Men,49/54Cm Frame Road Bicycle,700C",
        "rider_id": rider1.id
    }
    response = rider1_client.post(
        "/api/rider/bike/create",
        json=json
    )
    assert response.status_code == 200
    assert response.json().get('is_retired') is False


def test_create_bike_invalid_type(rider1_client, rider1, db):
    json = {
        "name": "Amazon Special",
        "type": "fat bike",
        "brand": "Eurobike",
        "model": "XC550 Road Bike,21 Speed Bikes for Women and Men,49/54Cm Frame Road Bicycle,700C",
        "rider_id": rider1.id
    }
    response = rider1_client.post(
        "/api/rider/bike/create",
        json=json
    )
    assert response.status_code == 422


def test_create_bike_duplicate(rider1_client, rider1, db):
    json = {
        "name": "Amazon Special",
        "type": BikeType.road.value,
        "brand": "Eurobike",
        "model": "XC550 Road Bike,21 Speed Bikes for Women and Men,49/54Cm Frame Road Bicycle,700C",
        "rider_id": rider1.id
    }
    response = rider1_client.post(
        "/api/rider/bike/create",
        json=json
    )
    assert response.status_code == 200
    response = rider1_client.post(
        "/api/rider/bike/create",
        json=json
    )
    assert response.status_code == 403


def test_update_bike(rider1_client, rider1, db, bike_road):
    json = {
        "name": "Amazon Special",
        "type": BikeType.road.value,
        "brand": "Eurobike",
        "model": "XC550 Road Bike,21 Speed Bikes for Women and Men,49/54Cm Frame Road Bicycle,700C",
    }
    response = rider1_client.patch(
        f"/api/rider/bike/{bike_road.id}",
        params={"rider_id": rider1.id},
        json=json,
    )
    assert response.status_code == 200
    assert all((item in response.json().items() for item in json.items()))


def test_update_bike_invalid_is_retired(rider1_client, rider1, db, bike_road):
    json = {
        "is_retired": 123
    }
    response = rider1_client.patch(
        f"/api/rider/bike/{bike_road.id}",
        params={"rider_id": rider1.id},
        json=json
    )
    assert response.status_code == 422
