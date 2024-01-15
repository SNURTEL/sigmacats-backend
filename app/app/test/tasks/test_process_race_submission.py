from datetime import datetime

import pytest
import gpxo
import numpy as np

from app.tasks.process_race_result_submission import process_race_result_submission, interpolate_end_timestamp


def test_end_point_interpolation(
        sample_ride_gpx,
):
    """
    Test interpolation of end_point (used for checking, if the race has been completed)
    """
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
    """
    Test interpolation of end_point when not all laps have been completed
    """
    ride = gpxo.Track(sample_ride_gpx)
    track_end = np.array([52.219954, 21.011319])  # last trackpoint in file
    interpolated = interpolate_end_timestamp(ride, track_end, no_laps=1)
    assert interpolated > datetime.fromisoformat('2024-01-08T20:50:00.412Z').replace(tzinfo=None)
    assert interpolated < datetime.fromisoformat('2024-01-08T20:50:02.618Z').replace(tzinfo=None)


def test_end_point_interpolation_too_many_laps(
        sample_ride_gpx
):
    """
    Test interpolation of end_point when there were too many laps completed
    """
    ride = gpxo.Track(sample_ride_gpx)
    track_end = np.array([52.219954, 21.011319])  # last trackpoint in file
    with pytest.raises(ValueError):
        interpolate_end_timestamp(ride, track_end, no_laps=99)


def test_end_point_interpolation_broken_race_end(
        sample_ride_gpx
):
    """
    Test interpolation of end_point in case of a failure
    """
    ride = gpxo.Track(sample_ride_gpx)
    track_end = np.array([0., 0.])  # last trackpoint in file
    with pytest.raises(ValueError):
        interpolate_end_timestamp(ride, track_end, no_laps=99)


def test_process_submission(
        race_in_progress_with_rider_and_participation,
        db, sample_ride_gpx, sample_track_gpx):
    """
    Test submission of a route covered by a rider during a race
    """
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
    """
    Test implemented strategy for failed submission of a route covered by a rider during a race
    """
    broken_gpx = \
        """<?xml version="1.0" encoding="UTF-8"?>
            <gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xmlns="http://www.topografix.com/GPX/1/1"
              xsi:schemaLocation="http://www.topografix.com/GPX/1/1
               http://www.topografix.com/GPX/1/1/gpx.xsd
                http://www.garmin.com/xmlschemas/GpxExtensions/v3
                 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd
                  http://www.garmin.com/xmlschemas/TrackPointExtension/v1
                   http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd
                    http://www.topografix.com/GPX/gpx_style/0/2
                     http://www.topografix.com/GPX/gpx_style/0/2/gpx_style.xsd"
                      xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
                       xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
                        xmlns:gpx_style="http://www.topografix.com/GPX/gpx_style/0/2"
                         version="1.1" creator="https://gpx.studio">
            <metadata>
                <name>new</name>
            </metadata>
            <trk>
                <name>new</name>
                <type>Cycling</type>
                <trkseg>
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
