from typing import Callable, Optional

from sqlmodel import Session, select

from app.core.celery import celery_app
from app.db.session import get_db
from app.tasks.recalculate_classification_scores import recalculate_classification_scores
from app.models.race import Race
from app.models.bike import BikeType
from app.models.season import Season
from app.models.account import Gender
from app.models.classification import Classification
from app.models.race_participation import RaceParticipation, RaceParticipationStatus
from app.models.ride_participation_classification_place import RiderParticipationClassificationPlace
from app.util.log import get_logger

logger = get_logger()

"""
This file contains a Celery task for assigning rider 
places in classifications within one race.
"""

@celery_app.task()
def assign_places_in_classifications(
        race_id: int,
        db: Optional[Session] = None
) -> None:
    """
    Assignment of places in classification
    """
    logger.info(f"Granting points for race {race_id}")

    if not db:
        db = next(get_db())

    race = db.get(Race, race_id)

    if not race:
        raise ValueError(f"Race {race_id} not found")

    general_classification: Classification = db.exec(
        select(Classification).where(Classification.name == "Klasyfikacja generalna",
                                     Classification.season == race.season)
    ).first()  # type: ignore[assignment]
    road_classification: Classification = db.exec(
        select(Classification).where(Classification.name == "Szosa", Classification.season == race.season)
    ).first()  # type: ignore[assignment]
    fixie_classification: Classification = db.exec(
        select(Classification).where(Classification.name == "Ostre koło", Classification.season == race.season)
    ).first()  # type: ignore[assignment]
    men_classification: Classification = db.exec(
        select(Classification).where(Classification.name == "Mężczyźni", Classification.season == race.season)
    ).first()  # type: ignore[assignment]
    women_classification: Classification = db.exec(
        select(Classification).where(Classification.name == "Kobiety", Classification.season == race.season)
    ).first()  # type: ignore[assignment]

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

    for e in (general_classification_race_entries + road_classification_race_entries
              + fixie_classification_race_entries + men_classification_race_entries
              + women_classification_race_entries):
        db.add(e)

    db.commit()

    season = db.exec(
        select(Season)
        .order_by(Season.start_timestamp.desc())  # type: ignore[attr-defined]
    ).first()

    if not season:
        logger.warning("Could not find current season. Scores will NOT be recalculated.")
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
    """
    Create race classification entries from general classification
    only including entries matching `filter` condition.
    """
    race_classification_entries = []
    offset = 0
    for participation in sorted(participations,
                                key=lambda p: p.place_assigned_overall):  # type: ignore[arg-type, return-value]
        if not filter(participation):
            offset += 1
            continue

        race_classification_entries.append(
            RiderParticipationClassificationPlace(
                classification=classification,
                race_participation=participation,
                place=participation.place_assigned_overall - offset if participation.place_assigned_overall else 99999
            )
        )

    return race_classification_entries
