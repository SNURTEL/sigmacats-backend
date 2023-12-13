from app.models.race_participation import RaceParticipation, RaceParticipationStatus
from app.models.bike import Bike, BikeType
from app.models.rider import Rider, RiderRead
from app.models.season import Season
from app.models.classification import Classification, ClassificationRead
from app.models.race import Race, RaceStatus, RaceTemperature, RaceRain, RaceWind
from app.models.race_bonus import RaceBonus
from app.models.account import Account, Gender, AccountType
from app.models.ride_participation_classification_place import RiderParticipationClassificationPlace
from app.models.rider_classification_link import RiderClassificationLink
from app.util.log import get_logger

logger = get_logger()

# if you are getting "TypeError: issubclass() arg 1 must be a class" from pydantic, models forward refs need to be
# updated

# If you have multiple refs to update in one model, update all of them in one call


def update_forward_refs():
    logger.info("Setting up forward refs...")

    Account.update_forward_refs(
        Rider=Rider,
        Gender=Gender,
        AccountType=AccountType
    )

    Bike.update_forward_refs(
        Rider=Rider,
        RaceParticipation=RaceParticipation,
        BikeType=BikeType
    )

    # Classification.update_forward_refs(
    #     Season=Season,
    #     Rider=Rider,
    #     RiderClassificationLink=RiderClassificationLink,
    #     RiderParticipationClassificationPlace=RiderParticipationClassificationPlace
    # )

    Race.update_forward_refs(
        Season=Season,
        RaceBonus=RaceBonus,
        RaceParticipation=RaceParticipation,
        RaceStatus=RaceStatus,
        RaceTemperature=RaceTemperature,
        RaceRain=RaceRain,
        RaceWind=RaceWind
    )

    RaceBonus.update_forward_refs(
        Race=Race
    )

    RaceParticipation.update_forward_refs(
        Rider=Rider,
        Race=Race,
        Bike=Bike,
        RiderParticipationClassificationPlace=RiderParticipationClassificationPlace,
        RaceParticipationStatus=RaceParticipationStatus
    )

    RiderParticipationClassificationPlace.update_forward_refs(
        RaceParticipation=RaceParticipation,
        Classification=Classification
    )

    Rider.update_forward_refs(
        Account=Account,
        Bike=Bike,
        Classification=Classification,
        RaceParticipation=RaceParticipation,
        RiderClassificationLink=RiderClassificationLink
    )

    RiderClassificationLink.update_forward_refs(
        Rider=Rider,
        Classification=Classification
    )

    Season.update_forward_refs(
        Classification=Classification,
        Race=Race
    )

    RiderRead.update_forward_refs(
        Account=Account,
        # Classification=Classification,
        # RaceParticipation=RaceParticipation,
        # Bike=Bike
    )
    ClassificationRead.update_forward_refs(
        RiderParticipationClassificationPlace=RiderParticipationClassificationPlace,
        Season=Season,
        Rider=Rider
    )

    logger.info("Forward refs done!")