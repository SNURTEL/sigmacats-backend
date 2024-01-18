import json
from typing import Sequence

from sqlmodel import select, Session

from app.tasks.recalculate_classification_scores import recalculate_classification_scores
from app.models.race import RaceStatus, RaceWind, RaceRain, RaceTemperature
from app.models.race_participation import RaceParticipationStatus
from app.models.bike import BikeType
from app.models.account import Gender
from app.models.season import Season
from app.models.classification import Classification
from app.models.rider_classification_link import RiderClassificationLink


def _get_classification_entries(classification: Classification, season_1: Season, db: Session) -> Sequence[
    RiderClassificationLink
]:
    """
    Get current classification entries from database
    """
    return db.exec(
        select(RiderClassificationLink)
        .join(Classification, RiderClassificationLink.classification_id == Classification.id)  # type: ignore[arg-type]
        .where(
            Classification.season_id == season_1.id,
            RiderClassificationLink.classification_id == classification.id
        )
    ).all()


def test_recalculate_classification_scores_general(
        riders_with_bikes, race_factory, classifications,
        race_participations_factory, race_classification_entries_factory, season_1, db
):
    """
    Test recalculation of general classification
    """
    riders, bikes = riders_with_bikes
    (r1, r2, r3, r4) = riders
    (b1, b2, b3, b4) = bikes

    race1 = race_factory(
        season=season_1,
        status=RaceStatus.ended,
        place_to_points_mapping_json=json.dumps([
            {"place": 1, "points": 100},
            {"place": 4, "points": 10},
        ])
    )
    race2 = race_factory(
        season=season_1,
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

    db.add_all([race1, *race1_participations, *race1_general_classification_entries,
                race2, *race2_participations, *race2_general_classification_entries])
    db.commit()

    recalculate_classification_scores(
        season_id=season_1.id, db=db
    )

    classification_scores = _get_classification_entries(classifications['general'], season_1, db)

    assert len(classification_scores) == 4
    rider_id_to_points_mapping = {
        r1.id: 600, r2.id: 1010, r3.id: 1010, r4.id: 1010
    }
    for cs in classification_scores:
        assert cs.score == rider_id_to_points_mapping[cs.rider_id]


def test_recalculate_classification_scores_bike_type(
        riders_with_bikes, race_factory, classifications,
        race_participations_factory, race_classification_entries_factory, season_1, db
):
    """
    Test recalculation of classification for given bike types
    """
    riders, bikes = riders_with_bikes
    (r1, r2, r3, r4) = riders
    (b1, b2, b3, b4) = bikes

    b2.type = BikeType.fixie
    b3.type = BikeType.fixie
    db.add_all([b2, b3])
    db.commit()
    db.refresh(b2)
    db.refresh(b3)

    race1 = race_factory(
        season=season_1,
        status=RaceStatus.ended,
        place_to_points_mapping_json=json.dumps([
            {"place": 1, "points": 1000},
            {"place": 2, "points": 100},
        ])
    )

    race1_participations = race_participations_factory(
        race=race1,
        riders=riders,
        bikes=(b1, b2, b3, b4),
        statuses=[RaceParticipationStatus.approved for _ in range(4)],
        entry_kwargs=[{"place_assigned_overall": p} for p in [1, 2, 3, 4]]
    )
    race1_classification_entries = race_classification_entries_factory(
        classification=classifications['road'],
        race_participations=[race1_participations[0], race1_participations[3]],
        places=[1, 2]
    ) + race_classification_entries_factory(
        classification=classifications['fixie'],
        race_participations=[race1_participations[1], race1_participations[2]],
        places=[1, 2]
    )

    db.add_all([race1, *race1_participations, *race1_classification_entries])
    db.commit()

    recalculate_classification_scores(
        season_id=season_1.id, db=db
    )

    road_classification_scores = _get_classification_entries(classifications['road'], season_1, db)
    road_rider_id_to_points_mapping = {
        r1.id: 1000, r2.id: 0, r3.id: 0, r4.id: 100
    }
    assert len(road_classification_scores) == 4
    for cs in road_classification_scores:
        assert cs.score == road_rider_id_to_points_mapping[cs.rider_id]

    fixie_classification_scores = _get_classification_entries(classifications['fixie'], season_1, db)
    fixie_rider_id_to_points_mapping = {
        r1.id: 0, r2.id: 1000, r3.id: 100, r4.id: 0
    }
    assert len(fixie_classification_scores) == 4
    for cs in fixie_classification_scores:
        assert cs.score == fixie_rider_id_to_points_mapping[cs.rider_id]


def test_recalculate_classification_scores_men_women(
        riders_with_bikes, race_factory, classifications,
        race_participations_factory, race_classification_entries_factory, season_1, db
):
    """
    Test recalculation of classification for a given gender
    """
    riders, bikes = riders_with_bikes
    (r1, r2, r3, r4) = riders
    (b1, b2, b3, b4) = bikes

    r1.account.gender = Gender.male
    r2.account.gender = Gender.female
    r3.account.gender = Gender.female
    r4.account.gender = Gender.male
    db.add_all([r1, r2, r3, r4])
    db.commit()
    for rider in riders:
        db.refresh(rider)

    race1 = race_factory(
        season=season_1,
        status=RaceStatus.ended,
        place_to_points_mapping_json=json.dumps([
            {"place": 1, "points": 1000},
            {"place": 2, "points": 100},
        ])
    )

    race1_participations = race_participations_factory(
        race=race1,
        riders=(r1, r2, r3, r4),
        bikes=bikes,
        statuses=[RaceParticipationStatus.approved for _ in range(4)],
        entry_kwargs=[{"place_assigned_overall": p} for p in [1, 2, 3, 4]]
    )
    race1_classification_entries = race_classification_entries_factory(
        classification=classifications['men'],
        race_participations=[race1_participations[0], race1_participations[3]],
        places=[1, 2]
    ) + race_classification_entries_factory(
        classification=classifications['women'],
        race_participations=[race1_participations[1], race1_participations[2]],
        places=[1, 2]
    )

    db.add_all([race1, *race1_participations, *race1_classification_entries])
    db.commit()

    recalculate_classification_scores(
        season_id=season_1.id, db=db
    )

    road_classification_scores = _get_classification_entries(classifications['men'], season_1, db)
    road_rider_id_to_points_mapping = {
        r1.id: 1000, r2.id: 0, r3.id: 0, r4.id: 100
    }
    assert len(road_classification_scores) == 2
    for cs in road_classification_scores:
        assert cs.score == road_rider_id_to_points_mapping[cs.rider_id]

    fixie_classification_scores = _get_classification_entries(classifications['women'], season_1, db)
    fixie_rider_id_to_points_mapping = {
        r1.id: 0, r2.id: 1000, r3.id: 100, r4.id: 0
    }
    assert len(fixie_classification_scores) == 2
    for cs in fixie_classification_scores:
        assert cs.score == fixie_rider_id_to_points_mapping[cs.rider_id]


def test_recalculate_classification_scores_weather_multipliers(
        riders_with_bikes, race_factory, classifications,
        race_participations_factory, race_classification_entries_factory, season_1, db
):
    """
    Test recalculatoin of classification for weather multipliers
    """
    riders, bikes = riders_with_bikes
    (r1, r2, r3, r4) = riders
    (b1, b2, b3, b4) = bikes

    race1 = race_factory(
        season=season_1,
        status=RaceStatus.ended,
        place_to_points_mapping_json=json.dumps([
            {"place": 1, "points": 100},
        ]),
        temperature=RaceTemperature.cold

    )
    race2 = race_factory(
        season=season_1,
        status=RaceStatus.ended,
        place_to_points_mapping_json=json.dumps([
            {"place": 1, "points": 100},
        ]),
        wind=RaceWind.heavy,
        rain=RaceRain.heavy
    )

    race1_participations = race_participations_factory(
        race=race1,
        riders=[r1],
        bikes=[b1],
        statuses=[RaceParticipationStatus.approved],
        entry_kwargs=[{"place_assigned_overall": 1}]
    )
    race1_general_classification_entries = race_classification_entries_factory(
        classification=classifications['general'],
        race_participations=[race1_participations[0]],
        places=[1]
    )
    race2_participations = race_participations_factory(
        race=race2,
        riders=[r1],
        bikes=[b1],
        statuses=[RaceParticipationStatus.approved],
        entry_kwargs=[{"place_assigned_overall": 1}]
    )
    race2_general_classification_entries = race_classification_entries_factory(
        classification=classifications['general'],
        race_participations=[race2_participations[0]],
        places=[1]
    )

    db.add_all([race1, *race1_participations, *race1_general_classification_entries,
                race2, *race2_participations, *race2_general_classification_entries])
    db.commit()

    recalculate_classification_scores(
        season_id=season_1.id, db=db
    )

    classification_scores = _get_classification_entries(classifications['general'], season_1, db)

    assert len(classification_scores) == 1
    rider_id_to_points_mapping = {
        r1.id: round(100 * 1.3 + 100 * 1.4 * 2.0)
    }
    for cs in classification_scores:
        assert cs.score == rider_id_to_points_mapping[cs.rider_id]
