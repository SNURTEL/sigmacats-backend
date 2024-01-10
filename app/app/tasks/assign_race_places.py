from datetime import datetime

import gpxo
import numpy as np
import pandas as pd
from scipy.signal import argrelmin
from fastapi import Depends
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from app.core.celery import celery_app
from app.db.session import get_db
from app.models.race import Race, RaceStatus
from app.models.race_participation import RaceParticipation
from app.util.log import get_logger

logger = get_logger()


@celery_app.task()
def assign_places(
    race_id: int,
    db: Session = None
):
    race = db.get(Race, race_id)
    race.status = RaceStatus.ended

    now = datetime.now()

    for p in race.race_participations:
        if not p.ride_end_timestamp:
            p.ride_end_timestamp = now
            db.add(p)

    db.commit()
    db.refresh(race)

    prev_timestamp = None
    prev_place = 1
    for i, p in enumerate(sorted(race.race_participations, key=lambda p: p.ride_end_timestamp), start=1):
        if p.ride_end_timestamp == prev_timestamp:
            p.place_generated_overall = prev_place
        else:
            p.place_generated_overall = i
        db.add(p)
        prev_timestamp = p.ride_end_timestamp
        prev_place = p.place_generated_overall

    db.add(race)
    db.commit()
