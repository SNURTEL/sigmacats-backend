from fastapi.encoders import jsonable_encoder

from app.models.rider import RiderRead
from app.models.classification import ClassificationRead


def test_classification_list_riders(rider1_client, db, classification_with_rider, rider1):
    response = rider1_client.get(f"/api/rider/classification/{classification_with_rider.id}/rider")
    assert response.status_code == 200
    assert response.json() == [jsonable_encoder(RiderRead.from_orm(rider1))]


def test_classification_list_no_classification_404(rider1_client, db):
    response = rider1_client.get("/api/rider/classification/3438948973/rider")
    assert response.status_code == 404


def test_classification_list_no_riders_404(rider1_client, classification_without_rider, db):
    response = rider1_client.get(f"/api/rider/classification/{classification_without_rider.id}/rider")
    assert response.status_code == 404


def test_season_list_classification(rider1_client, db, classification_with_rider, season):
    response = rider1_client.get(f"/api/rider/season/{season.id}/classification")
    assert response.status_code == 200
    assert response.json() == [jsonable_encoder(ClassificationRead.from_orm(classification_with_rider))]


def test_season_list_no_classifications_404(rider1_client, db):
    response = rider1_client.get("/api/rider/season/457475894/classification")
    assert response.status_code == 404