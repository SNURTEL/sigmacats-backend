import datetime

from fastapi.encoders import jsonable_encoder

from app.models.rider import RiderRead
from app.models.classification import ClassificationRead
from app.models.season import SeasonRead
from app.models.rider_classification_link import RiderClassificationLinkRead, RiderClassificationLinkRiderDetails
from app.test.fixtures import NOVEMBER_TIME


def test_classification_list_riders(rider1_client, db, classification_with_rider, rider1):
    """
    Test listing of classification with a given rider
    """
    response = rider1_client.get(f"/api/rider/classification/{classification_with_rider.id}/rider")
    assert response.status_code == 200
    assert response.json() == [jsonable_encoder(RiderRead.from_orm(rider1))]


def test_classification_list_no_classification_404(rider1_client, db):
    """
    Test listing of an non-existing classifcation
    """
    response = rider1_client.get("/api/rider/classification/3438948973/rider")
    assert response.status_code == 404


def test_classification_list_no_riders_404(rider1_client, classification_without_rider, db):
    """
    Test listing of a classification without riders
    """
    response = rider1_client.get(f"/api/rider/classification/{classification_without_rider.id}/rider")
    assert response.status_code == 404


def test_season_list_classification(rider1_client, db, classification_with_rider, season_1):
    """
    Test listing of a season classification
    """
    response = rider1_client.get(f"/api/rider/season/{season_1.id}/classification")
    assert response.status_code == 200
    assert response.json() == [jsonable_encoder(ClassificationRead.from_orm(classification_with_rider))]


def test_season_list_no_classifications_404(rider1_client, db):
    """
    Test lising of a non-existing season classification
    """
    response = rider1_client.get("/api/rider/season/457475894/classification")
    assert response.status_code == 404


def test_season_current(rider1_client, season_1, db, patch_datetime_now):
    """
    Test listing of a current season
    """
    response = rider1_client.get("/api/rider/season/current")
    assert datetime.datetime.now() == NOVEMBER_TIME
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(SeasonRead.from_orm(season_1))


def test_season_all(rider1_client, db, season_1, season_2):
    """
    Test listing of all seasons
    """
    seasons = [jsonable_encoder(SeasonRead.from_orm(season)) for season in [season_1, season_2]]
    response = rider1_client.get("/api/rider/season/all")
    assert response.status_code == 200
    for season in seasons:
        assert season in response.json()


def test_rider_classification_link_classification_id(
        rider1_client,
        classification_with_rider,
        rider_classification_link_rider_details,
        db):
    """
    Test linking between rider and classification
    """
    response = rider1_client.get(f"/api/rider/rider_classification_link/{classification_with_rider.id}/classification")
    assert response.status_code == 200
    assert response.json() == [
        jsonable_encoder(RiderClassificationLinkRiderDetails.from_orm(rider_classification_link_rider_details))
    ]


def test_rider_classification_link_no_classification_404(
        rider1_client,
        db):
    """
    Test linking between rider and classification when there is no classification
    """
    response = rider1_client.get("/api/rider/rider_classification_link/934789374893897/classification")
    assert response.status_code == 404


def test_rider_classification_link_no_rider_in_classification_404(
        rider1_client,
        classification_without_rider
        ):
    """
    Test linking between rider and classification when rider is not in a given classification
    """
    response = rider1_client.get(
        f"/api/rider/rider_classification_link/{classification_without_rider.id}/classification"
    )
    assert response.status_code == 404


def test_rider_classification_link_rider_id(
        rider1_client,
        rider1,
        rider_classification_link,
        db):
    """
    Test returning of a classification for a given rider_classification_link
    """
    response = rider1_client.get(f"/api/rider/rider_classification_link/{rider1.id}/rider")
    assert response.status_code == 200
    assert response.json() == [jsonable_encoder(RiderClassificationLinkRead.from_orm(rider_classification_link))]


def test_rider_classification_link_no_rider_404(
        rider1_client,
        db):
    """
    Test link between rider and classification when there is no rider
    """
    response = rider1_client.get("/api/rider/rider_classification_link/934789374893897/rider")
    assert response.status_code == 404
