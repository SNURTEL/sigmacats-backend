import shutil
from datetime import datetime

import pytest
import gpxo
import numpy as np
import pandas as pd

from app.tasks.process_race_result_submission import process_race_result_submission, interpolate_end_timestamp
from app.models.race import RaceStatus
from app.models.race_participation import RaceParticipationStatus, RaceParticipation


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


def test_end_point_interpolation(
    sample_ride_gpx,
):
    ride = gpxo.Track(sample_ride_gpx)
    with open(sample_ride_gpx) as fp:
        print(fp.read())
    print(ride)
    track_end = np.array([52.219954, 21.011319])  # last trackpoint in file
    interpolated = interpolate_end_timestamp(ride, track_end, no_laps=3)
    assert interpolated < datetime.fromisoformat('2024-01-08T20:53:39.570Z').replace(tzinfo=None)
    assert interpolated > datetime.fromisoformat('2024-01-08T20:53:38.767Z').replace(tzinfo=None)



def test_end_point_interpolation_fewer_laps(
    sample_ride_gpx
):
    ride = gpxo.Track(sample_ride_gpx)
    track_end = np.array([52.219954, 21.011319])  # last trackpoint in file
    interpolated = interpolate_end_timestamp(ride, track_end, no_laps=1)
    assert interpolated > datetime.fromisoformat('2024-01-08T20:50:00.412Z').replace(tzinfo=None)
    assert interpolated < datetime.fromisoformat('2024-01-08T20:50:02.618Z').replace(tzinfo=None)


def test_end_point_interpolation_too_many_laps(
    sample_ride_gpx
):
    ride = gpxo.Track(sample_ride_gpx)
    track_end = np.array([52.219954, 21.011319])  # last trackpoint in file
    with pytest.raises(ValueError):
        interpolate_end_timestamp(ride, track_end, no_laps=99)


def test_end_point_interpolation_broken_race_end(
    sample_ride_gpx
):
    ride = gpxo.Track(sample_ride_gpx)
    track_end = np.array([0., 0.])  # last trackpoint in file
    with pytest.raises(ValueError):
        interpolate_end_timestamp(ride, track_end, no_laps=99)


def test_process_submission(
        race_in_progress_with_rider_and_participation,
        db, sample_ride_gpx, sample_track_gpx):

    race, participation, rider, bike = race_in_progress_with_rider_and_participation

    process_race_result_submission(
        race_id=race.id,
        rider_id=rider.id,
        recording_filepath=sample_ride_gpx,
        db=db)

    ride = gpxo.Track(sample_ride_gpx)
    ride_start_timestamp = ride.data.head(1).index.to_pydatetime()[0]
    ride_end_timestamp = ride.data.tail(1).index.to_pydatetime()[0]

    db.refresh(participation)

    assert participation.ride_gpx_file == sample_ride_gpx
    assert participation.ride_start_timestamp == ride_start_timestamp
    assert participation.ride_end_timestamp < ride_end_timestamp


def test_process_fallback_strategy(
        race_in_progress_with_rider_and_participation,
        db, sample_ride_gpx):


    broken_gpx = \
    """<?xml version="1.0" encoding="UTF-8"?>
        <gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd http://www.topografix.com/GPX/gpx_style/0/2 http://www.topografix.com/GPX/gpx_style/0/2/gpx_style.xsd" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:gpx_style="http://www.topografix.com/GPX/gpx_style/0/2" version="1.1" creator="https://gpx.studio">
        <metadata>
            <name>new</name>
        </metadata>
        <trk>
            <name>new</name>
            <type>Cycling</type>
            <trkseg>
            <trkpt lat="52.219960373107334" lon="21.011253297328953">
                <ele>115.9</ele>
                <time>2024-01-08T20:42:42.000Z</time>
            </trkpt>
            </trkseg>
        </trk>
    </gpx>
    """

    race, participation, rider, bike = race_in_progress_with_rider_and_participation

    with open(sample_ride_gpx, mode='w') as fp:
        fp.write(broken_gpx)

    now = datetime.now()

    process_race_result_submission(
        race_id=race.id,
        rider_id=rider.id,
        recording_filepath=sample_ride_gpx,
        db=db)

    db.refresh(participation)

    assert participation.ride_start_timestamp == race.start_timestamp
    assert participation.ride_end_timestamp >= now.replace(microsecond=0)
