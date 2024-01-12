import json
from datetime import datetime
from typing import Callable

from sqlmodel import Session, select

from app.core.celery import celery_app
from app.db.session import get_db
from app.tasks.recalculate_classification_scores import recalculate_classification_scores
from app.models.race import Race, RaceStatus
from app.models.bike import BikeType
from app.models.season import Season
from app.models.account import Gender
from app.models.classification import Classification
from app.models.race_participation import RaceParticipation, RaceParticipationStatus
from app.models.ride_participation_classification_place import RiderParticipationClassificationPlace
from app.util.log import get_logger

logger = get_logger()


@celery_app.task()
def assign_places_in_classifications(
        race_id: int,
        db: Session = None
):
    logger.info(f"Granting points for race {race_id}")

    if not db:
        db = next(get_db())

    race = db.get(Race, race_id)

    general_classification = db.exec(
        select(Classification).where(Classification.name == "Klasyfikacja generalna",
                                     Classification.season == race.season)
    ).first()
    road_classification = db.exec(
        select(Classification).where(Classification.name == "Szosa", Classification.season == race.season)
    ).first()
    fixie_classification = db.exec(
        select(Classification).where(Classification.name == "Ostre koło", Classification.season == race.season)
    ).first()
    men_classification = db.exec(
        select(Classification).where(Classification.name == "Mężczyźni", Classification.season == race.season)
    ).first()
    women_classification = db.exec(
        select(Classification).where(Classification.name == "Kobiety", Classification.season == race.season)
    ).first()

    classificaitons = [general_classification, road_classification, fixie_classification, men_classification,
                       women_classification]
    if not all([general_classification, road_classification, fixie_classification, men_classification,
                women_classification]):
        raise ValueError(f"Could not find all classifications: {classificaitons}")

    participations = [p for p in race.race_participations if p.status == RaceParticipationStatus.approved]

    general_classification_race_entries = create_race_classification_entries(
        classification=general_classification,
        participations=participations,
        filter=lambda _: True
    )

    road_classification_race_entries = create_race_classification_entries(
        classification=road_classification,
        participations=participations,
        filter=lambda p: p.bike.type == BikeType.road
    )

    fixie_classification_race_entries = create_race_classification_entries(
        classification=fixie_classification,
        participations=participations,
        filter=lambda p: p.bike.type == BikeType.fixie
    )

    men_classification_race_entries = create_race_classification_entries(
        classification=men_classification,
        participations=participations,
        filter=lambda p: p.rider.account.gender == Gender.male
    )

    women_classification_race_entries = create_race_classification_entries(
        classification=women_classification,
        participations=participations,
        filter=lambda p: p.rider.account.gender == Gender.female
    )

    for e in general_classification_race_entries + \
             road_classification_race_entries + \
             fixie_classification_race_entries + \
             men_classification_race_entries + \
             women_classification_race_entries:
        db.add(e)

    db.commit()

    now = datetime.now()
    season = db.exec(
        select(Season)
        .where(Season.start_timestamp <= now,
               Season.end_timestamp is None)
    ).first()

    if not season:
        logger.warning(f"Could not find current season for current date {now}. Scores will NOT be recalculated.")
    else:
        recalculate_classification_scores.delay(
            season_id=season.id
        )

    logger.info("Task done!")


def create_race_classification_entries(
        classification: Classification,
        participations: list[RaceParticipation],
        filter: Callable[[RaceParticipation], bool]
) -> list[RiderParticipationClassificationPlace]:
    race_classification_entries = []
    offset = 0
    for participation in sorted(participations, key=lambda p: p.place_assigned_overall):
        if not filter(participation):
            offset += 1
            continue

        race_classification_entries.append(
            RiderParticipationClassificationPlace(
                classification=classification,
                race_participation=participation,
                place=participation.place_assigned_overall - offset
            )
        )

    return race_classification_entries
