from typing import Optional
from datetime import datetime

import gpxo
import numpy as np
import pandas as pd
from scipy.signal import argrelmin
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from app.core.celery import celery_app
from app.tasks.generate_race_places import end_race_and_generate_places
from app.db.session import get_db
from app.models.race import Race
from app.models.race_participation import RaceParticipation, RaceParticipationStatus
from app.util.log import get_logger

FINISH_DISTANCE_THRESHOLD = 0.00015

logger = get_logger()


@celery_app.task()
def process_race_result_submission(
        race_id: int,
        rider_id: int,
        recording_filepath: str,
        db: Optional[Session] = None
) -> None:
    logger.info(f"Received participation task for race_id={race_id}, rider_id={rider_id}")

    if not db:
        db = next(get_db())

    race = db.get(Race, race_id)

    if not race:
        raise ValueError(f"Race {race_id} not found")

    stmt: SelectOfScalar = (
        select(RaceParticipation)
        .where(
            RaceParticipation.race_id == race_id,
            RaceParticipation.rider_id == rider_id
        )
    )
    race_participation = db.exec(stmt).first()

    if not race_participation:
        raise ValueError(f"Race participation for race_id={race_id} ider_id{rider_id} not found")

    recording = gpxo.Track(recording_filepath)
    track = gpxo.Track(race.checkpoints_gpx_file)

    try:
        start_timestamp = recording.data.head(1).index.to_pydatetime()[0]
    except (ValueError, IndexError, KeyError, TypeError) as e:
        logger.warning(
            f"Could not read start timestamp for participation race_id={race_id}, rider_id={rider_id}, "
            f"file={recording_filepath}. Falling back to race start.\n" + repr(
                e))
        start_timestamp = race.start_timestamp

    try:
        end_point = track.data.tail(1)[['latitude (°)', 'longitude (°)']].values.T.squeeze()
        end_timestamp = interpolate_end_timestamp(recording=recording, end_point=end_point, no_laps=race.no_laps)
    except (ValueError, IndexError, KeyError, TypeError) as e:
        logger.warning(
            f"Could not interpolate end timestamp for participation race_id={race_id}, rider_id={rider_id}, "
            f"file={recording_filepath}. Falling back to now().\n" + repr(
                e))
        end_timestamp = datetime.now()

    race_participation.ride_start_timestamp = start_timestamp
    race_participation.ride_end_timestamp = end_timestamp
    race_participation.ride_gpx_file = recording_filepath

    db.add(race_participation)
    db.commit()
    db.refresh(race_participation)

    logger.info("Task done!")

    stmt = (
        select(RaceParticipation)
        .where(
            RaceParticipation.race_id == race_id,
            RaceParticipation.status == RaceParticipationStatus.approved
        )
    )
    all_participations = db.exec(stmt).all()

    if all([p.ride_end_timestamp is not None for p in all_participations]):
        logger.info(f"Looks like all riders finished race {race_id} - closing and assigning places.")
        end_race_and_generate_places(race_id=race_id, db=db)

    return


def interpolate_end_timestamp(recording: gpxo.Track, end_point: np.ndarray, no_laps: int) -> datetime:
    if end_point.shape != (2,):
        raise ValueError(f'GPX processing error: end point coordinates have wrong shape ({end_point.shape})')

    # ensure recording has elevation data - gpxo requires it
    recording.elevation = np.zeros(recording.latitude.shape)

    recording.smooth(n=15)

    df = recording.data

    # calculate distance to track end point
    dist = df.apply(lambda r: np.linalg.norm(np.array([r['latitude (°)'], r['longitude (°)']]) - end_point),
                    axis='columns')
    # find points locally closest to track end
    indices = argrelmin(dist.values, order=5)[0]

    if len(indices) < 2:
        raise ValueError(f'GPX processing error: found less than 2 distance minima ({len(indices)})')

    merged = df.merge(dist.rename('dist'), left_index=True, right_index=True, validate='1:1')
    peaks = merged.iloc[indices]

    # filter out local minima not located near track's end
    filtered = peaks.loc[peaks.dist < FINISH_DISTANCE_THRESHOLD]

    if no_laps > len(filtered):
        raise ValueError("GPX contains fewer laps than specified")

    if filtered.empty:
        raise ValueError("No trackpoint in GPX is near race end point")

    # get trackpoint closest to end in final lap; use `min` in case recording in app starts with a delay
    closest = filtered.iloc[[min(max(no_laps, len(filtered)), no_laps + 1) - 1]]

    if closest.empty:
        raise ValueError('GPX processing error: could not find closest point')

    merged_with_timestamp = merged.assign(timestamp=merged.index)
    # sample neighbouring points to closes, discard one with the greatest dist
    samples = pd.concat([closest.assign(timestamp=closest.index), merged_with_timestamp.shift(1).loc[closest.index],
                         merged_with_timestamp.shift(-1).loc[closest.index]])
    p1, p2 = samples.nsmallest(2, columns='dist')[['latitude (°)', 'longitude (°)']].values
    t1, t2 = samples.nsmallest(2, columns='dist')['timestamp']

    # analytically find point between p1 and p2 closest to track end
    a1 = (p1[1] - p2[1]) / (p1[0] - p2[0] + 1e-12) + 1e-12
    b1 = (p1[1] - a1 * p1[0])
    a2 = -1 / a1
    b2 = end_point[1] - a2 * end_point[0]

    xp = (b2 - b1) / (a1 - a2)
    yp = a2 * xp + b2
    p_interpolated = np.array([xp, yp])

    p_first, p_second, t_first, t_second = (p1, p2, t1, t2) if t1 <= t2 else (p2, p1, t2, t1)

    # estimate timestamp for interpolated point
    delta_p = np.linalg.norm(p1 - p2)
    delta_t = t_second - t_first
    t_interpolated = t_first + delta_t * (np.linalg.norm(p_first - p_interpolated) / delta_p)

    if not t_first <= t_interpolated <= t_second:
        raise ValueError(
            f'GPX processing error: interpolated timestamp not between interpolation points '
            f'({t_first} <= {t_interpolated} <= {t_second})')

    return t_interpolated
