from app.models.race import *
from app.models.race_participation import *
from app.models.season import *
from app.models.race_bonus import *


# if you are getting "TypeError: issubclass() arg 1 must be a class" from pydantic, models forward refs need to be
# updated

# If you have multiple refs to update in one model, update all of them in one call


def update_forward_refs():
    RaceReadDetailRider.update_forward_refs(
        RaceBonusListRead=RaceBonusListRead,
        SeasonListRead=SeasonListRead,
        RaceParticipationListRead=RaceParticipationListRead)
    RaceReadListRider.update_forward_refs(
        RaceParticipationStatus=RaceParticipationStatus
    )
    RaceReadDetailCoordinator.update_forward_refs(
        RaceBonusListRead=RaceBonusListRead,
        SeasonListRead=SeasonListRead,
        RaceParticipationListRead=RaceParticipationListRead)
