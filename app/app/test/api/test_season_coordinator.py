from sqlmodel import select
from fastapi.encoders import jsonable_encoder

from app.models.season import SeasonRead
from app.models.classification import Classification


def test_coordinator_list_seasons(coordinator_client, db, season, season2):
    response = coordinator_client.get("/api/coordinator/season")
    assert response.status_code == 200
    assert [entry for entry in response.json() if int(entry['id']) > 10000] == [
        jsonable_encoder(SeasonRead.from_orm(item)) for item in
        (season2, season)]


def test_coordinator_season_detail(coordinator_client, db, season):
    response = coordinator_client.get(f"/api/coordinator/season/{season.id}")
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(SeasonRead.from_orm(season))


def test_coordinator_season_detail_404(coordinator_client, db):
    response = coordinator_client.get("/api/coordinator/season/54654246")
    assert response.status_code == 404


def test_coordinator_season_start_new(coordinator_client, db, season):
    response = coordinator_client.post("/api/coordinator/season/start-new",
                                       json={"name": "Test Season"})
    print(response.json())
    assert response.status_code == 201
    assert response.json()['name'] == "Test Season"

    classifications = db.exec(
        select(Classification).where(Classification.season_id == int(response.json()['id']))
    ).all()
    assert len(classifications) == 5


def test_coordinator_season_start_new_empty_name_400(coordinator_client, db, season):
    response = coordinator_client.post("/api/coordinator/season/start-new",
                                       json={"name": ""})
    print(response.json())
    assert response.status_code == 400
