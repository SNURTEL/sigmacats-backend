import shutil

import pytest

from app.models.race import RaceStatus
from app.models.race_participation import RaceParticipationStatus


def test_submit_race_result(
        rider1_client,
        race_in_progress_with_rider_and_participation,
        db, sample_ride_gpx,
        disable_celery_tasks,
        monkeypatch):
    monkeypatch.setattr(shutil, 'move', lambda *args, **kwargs: None)

    race, participation, rider, bike = race_in_progress_with_rider_and_participation

    response = rider1_client.post(
        f"/api/rider/race/{race.id}/upload-result",
        data={"fileobj.path": sample_ride_gpx}
    )

    assert response.status_code == 202


@pytest.mark.parametrize("client,code",
                         [
                             (pytest.lazy_fixture("client_unauthenticated"), 401),
                             (pytest.lazy_fixture("rider1_client"), 202),
                             (pytest.lazy_fixture("coordinator_client"), 403),
                             (pytest.lazy_fixture("admin_client"), 403)
                         ])
def test_submit_race_result_access(
        race_in_progress_with_rider_and_participation,
        db, sample_ride_gpx,
        disable_celery_tasks,
        monkeypatch,
        client,
        code):
    monkeypatch.setattr(shutil, 'move', lambda *args, **kwargs: None)

    race, participation, rider, bike = race_in_progress_with_rider_and_participation

    response = client.post(
        f"/api/rider/race/{race.id}/upload-result",
        data={"fileobj.path": sample_ride_gpx}
    )

    assert response.status_code == code


def test_submit_race_result_malformed_gpx_400(
        rider1_client,
        race_in_progress_with_rider_and_participation,
        db, sample_ride_gpx,
        disable_celery_tasks,
        monkeypatch):
    monkeypatch.setattr(shutil, 'move', lambda *args, **kwargs: None)

    race, participation, rider, bike = race_in_progress_with_rider_and_participation

    with open(sample_ride_gpx, mode='w') as fp:
        fp.write("This is certainly not a GPX file")

    response = rider1_client.post(
        f"/api/rider/race/{race.id}/upload-result",
        data={"fileobj.path": sample_ride_gpx}
    )

    assert response.status_code == 400


@pytest.mark.parametrize("status", [RaceStatus.pending, RaceStatus.cancelled, RaceStatus.ended])
def test_submit_race_result_incorrect_race_status_400(
        rider1_client,
        race_in_progress_with_rider_and_participation,
        db, sample_ride_gpx,
        disable_celery_tasks,
        monkeypatch,
        status):
    monkeypatch.setattr(shutil, 'move', lambda *args, **kwargs: None)

    race, participation, rider, bike = race_in_progress_with_rider_and_participation

    race.status = status
    db.add(race)
    db.commit()
    db.refresh(race)

    response = rider1_client.post(
        f"/api/rider/race/{race.id}/upload-result",
        data={"fileobj.path": sample_ride_gpx}
    )

    assert response.status_code == 400


def test_submit_race_result_not_participating_400(
        rider1_client,
        race_in_progress_with_rider_and_participation,
        db, sample_ride_gpx,
        disable_celery_tasks,
        monkeypatch):
    monkeypatch.setattr(shutil, 'move', lambda *args, **kwargs: None)

    race, participation, rider, bike = race_in_progress_with_rider_and_participation

    db.delete(participation)
    db.commit()
    db.refresh(race)

    response = rider1_client.post(
        f"/api/rider/race/{race.id}/upload-result",
        data={"fileobj.path": sample_ride_gpx}
    )

    assert response.status_code == 400


@pytest.mark.parametrize("status", [RaceParticipationStatus.pending, RaceParticipationStatus.rejected])
def test_submit_race_result_incorrect_participation_status_400(
        rider1_client,
        race_in_progress_with_rider_and_participation,
        db, sample_ride_gpx,
        disable_celery_tasks,
        monkeypatch,
        status):
    monkeypatch.setattr(shutil, 'move', lambda *args, **kwargs: None)

    race, participation, rider, bike = race_in_progress_with_rider_and_participation

    participation.status = status
    db.add(participation)
    db.commit()
    db.refresh(participation)

    response = rider1_client.post(
        f"/api/rider/race/{race.id}/upload-result",
        data={"fileobj.path": sample_ride_gpx}
    )

    assert response.status_code == 400


def test_submit_race_result_already_submitted(
        rider1_client,
        race_in_progress_with_rider_and_participation,
        db, sample_ride_gpx,
        disable_celery_tasks,
        monkeypatch):
    monkeypatch.setattr(shutil, 'move', lambda *args, **kwargs: None)

    race, participation, rider, bike = race_in_progress_with_rider_and_participation

    participation.ride_gpx_file = sample_ride_gpx
    db.add(participation)
    db.commit()
    db.refresh(participation)

    response = rider1_client.post(
        f"/api/rider/race/{race.id}/upload-result",
        data={"fileobj.path": sample_ride_gpx}
    )
    assert response.status_code == 400
