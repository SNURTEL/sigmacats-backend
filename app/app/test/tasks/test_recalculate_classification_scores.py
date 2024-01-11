import pytest
import json

from sqlmodel import select

from app.tasks.recalculate_classification_scores import recalculate_classification_scores
from app.models.race import RaceStatus, RaceReadDetailCoordinator, RaceReadListCoordinator
from app.models.race_participation import RaceParticipationStatus
from app.models.classification import Classification
from app.models.rider_classification_link import RiderClassificationLink


def test_recalculate_classification_scores_general(
        riders_with_bikes, race_factory, classifications,
        race_participations_factory, race_classification_entries_factory, season, db
):
    riders, bikes = riders_with_bikes
    (r1, r2, r3, r4) = riders
    (b1, b2, b3, b4) = bikes

    race1 = race_factory(
        season=season,
        status=RaceStatus.ended,
        place_to_points_mapping_json=json.dumps([
            {"place": 1, "points": 100},
            {"place": 4, "points": 10},
        ])
    )
    race2 = race_factory(
        season=season,
        status=RaceStatus.ended,
        place_to_points_mapping_json=json.dumps([
            {"place": 3, "points": 1000},
            {"place": 999, "points": 500},
        ])
    )

    race1_places = [1, 2, 3, 4]
    race1_participations = race_participations_factory(
        race=race1,
        riders=riders,
        bikes=bikes,
        statuses=[RaceParticipationStatus.approved for _ in range(4)],
        entry_kwargs=[{"place_assigned_overall": p} for p in race1_places]
    )
    race1_general_classification_entries = race_classification_entries_factory(
        classification=classifications['general'],
        race_participations=race1_participations,
        places=race1_places
    )
    race2_places = [4, 3, 2, 1]
    race2_participations = race_participations_factory(
        race=race2,
        riders=riders,
        bikes=bikes,
        statuses=[RaceParticipationStatus.approved for _ in range(4)],
        entry_kwargs=[{"place_assigned_overall": p} for p in race1_places]
    )
    race2_general_classification_entries = race_classification_entries_factory(
        classification=classifications['general'],
        race_participations=race2_participations,
        places=race2_places
    )

    db.add_all([
        race1,
        *race1_participations,
        *race1_general_classification_entries,
        race2,
        *race2_participations,
        *race2_general_classification_entries
    ])
    db.commit()

    recalculate_classification_scores(
        season_id=season.id, db=db
    )

    classification_scores = db.exec(
        select(RiderClassificationLink)
        .join(Classification, RiderClassificationLink.classification_id == Classification.id)
        .where(
            Classification.season_id == season.id,
            RiderClassificationLink.classification_id == classifications['general'].id
        )
    ).all()

    assert len(classification_scores) == 4
    rider_id_to_points_mapping = {
        r1.id: 600, r2.id: 1010, r3.id: 1010, r4.id: 1010
    }
    for cs in classification_scores:
        assert cs.score == rider_id_to_points_mapping[cs.rider_id]

