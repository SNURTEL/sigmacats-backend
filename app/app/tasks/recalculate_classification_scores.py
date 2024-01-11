import json
import itertools
from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from app.core.celery import celery_app
from app.db.session import get_db
from app.util.log import get_logger
from app.models.race import Race, RaceStatus
from app.models.rider import Rider
from app.models.rider_classification_link import RiderClassificationLink
from app.models.account import Account, Gender
from app.models.season import Season
from app.models.classification import Classification
from app.models.race_participation import RaceParticipation, RaceParticipationStatus
from app.models.ride_participation_classification_place import RiderParticipationClassificationPlace

logger = get_logger()


@celery_app.task()
def recalculate_classification_scores(
        season_id: Optional[list[int]] = None,
        db: Session = None
):
    logger.info(f"Recalculating stats in season {season_id}")

    if not db:
        db = next(get_db())

    if season_id is None:
        now = datetime.now()
        season = db.exec(
            select(Season).where(
                Season.start_timestamp <= now,
                Season.end_timestamp > now
            )
        ).first()

    else:
        season = db.get(Season, season_id)

    general_classification = db.exec(
        select(Classification).where(Classification.name == "Klasyfikacja generalna",
                                     Classification.season == season)
    ).first()
    road_classification = db.exec(
        select(Classification).where(Classification.name == "Szosa", Classification.season == season)
    ).first()
    fixie_classification = db.exec(
        select(Classification).where(Classification.name == "Ostre koło", Classification.season == season)
    ).first()
    men_classification = db.exec(
        select(Classification).where(Classification.name == "Mężczyźni", Classification.season == season)
    ).first()
    women_classification = db.exec(
        select(Classification).where(Classification.name == "Kobiety", Classification.season == season)
    ).first()

    race_participations = db.exec(
        select(RaceParticipation)
        .join(Race,
              RaceParticipation.race_id == Race.id)
        .join(Rider,
              RaceParticipation.rider_id == Rider.id)
        .join(Account,
              RaceParticipation.rider_id == Account.id)
        .join(RiderParticipationClassificationPlace,
              RiderParticipationClassificationPlace.race_participation_id == RaceParticipation.id)
        .where(
            Race.season == season,
            Race.status == RaceStatus.ended,
            RaceParticipation.status == RaceParticipationStatus.approved
        )
    ).all()

    riders = []
    rider_ids = []
    for p in race_participations:
        if p.id not in rider_ids:
            riders.append(p.rider)
            rider_ids.append(p.id)
    classification_rider_scores = {
        general_classification.id: {r.id: 0 for r in riders},
        road_classification.id: {r.id: 0 for r in riders},
        fixie_classification.id: {r.id: 0 for r in riders},
        men_classification.id: {r.id: 0 for r in riders if r.account.gender == Gender.male},
        women_classification.id: {r.id: 0 for r in riders if r.account.gender == Gender.female}
    }

    for participation in race_participations:
        point_mapping = {item['place']: item['points'] for item in json.loads(participation.race.place_to_points_mapping_json)}
        for race_classification_place in participation.classification_places:
            try:
                print(race_classification_place)
                classification_rider_scores[race_classification_place.clasification_id][participation.rider_id] += get_points_for_place(
                    race_classification_place.place, point_mapping
                )
            except IndexError as e:
                logger.warning(
                    f"Could not set score for race participation {participation.id}(rider {participation.rider_id}, "
                    f"race {participation.race_id}) in classification {race_classification_place.classification_id} "
                    f"({race_classification_place.classification.name})\n " + repr(e))
                continue

    print(classification_rider_scores)
    logger.info("Task done!")

    old_classification_places = db.exec(
        select(RiderClassificationLink)
        .join(Classification, Classification.id == RiderClassificationLink.classification_id)
        .where(Classification.season_id == season_id)
    )
    for old in old_classification_places:
        db.delete(old)

    classification_places = [RiderClassificationLink(
        rider_id=rider_id,
        classification_id=classification_id,
        score=score
    ) for classification_id, rider_id, score in itertools.chain(*[[(c_id, k, v) for k, v in  c_dict.items()] for c_id, c_dict in classification_rider_scores.items()])]

    db.add_all(classification_places)
    db.commit()

    logger.info("Task done!")



def get_points_for_place(place_assigned: int, mapping: dict[int, int]):
    return next((points for place, points in mapping.items() if place >= place_assigned), 0)
