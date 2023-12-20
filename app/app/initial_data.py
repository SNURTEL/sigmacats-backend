from datetime import datetime

from app.models.account import Account
from app.models.rider import Rider
from app.models.bike import Bike, BikeType
from app.models.season import Season
from app.models.race import Race, RaceStatus, RaceTemperature, RaceRain
from app.models.race_bonus import RaceBonus
from app.models.race_participation import RaceParticipation, RaceParticipationStatus
from app.models.classification import Classification
from app.models.ride_participation_classification_place import RiderParticipationClassificationPlace
from app.models.rider_classification_link import RiderClassificationLink

bike_road = Bike(
    name="Rakieta",
    type=BikeType.road,
    brand="Canyon",
    model="Ultimate CFR eTap",
)

bike_fixie = Bike(
    name="Czarna strzała",
    type=BikeType.fixie,
    brand="FIXIE inc.",
    model="Floater Race",
)

# dummy_admin_account = Account(
#     type="admin",
#     username="dummy_admin",
#     name="Jane",
#     surname="Doe",
#     email="ja.doe@sigma.org",
#     password_hash="JSDHFGKIUSDFHBKGSBHDFKGS"
# )
#
# dummy_admin = Admin(
#     id=dummy_admin_account.id
# )

# dummy_coordinator_account = Account(
#     type="admin",
#     username="dummy_coordinator",
#     name="Richard",
#     surname="Roe",
#     email="ra.roe@sigma.org",
#     password_hash="JSDHFGKIUSDFHBKGSBHDFKGS"
# )
#
# dummy_coordinator = Coordinator(
#     id=dummy_coordinator_account.id,
#     phone_number="123456789"
# )

dummy_rider_account = Account(
    type="rider",
    username="dummy_rider",
    name="John",
    surname="Doe",
    email="jo.doe@sigma.org",
    hashed_password="JSDHFGKIUSDFHBKGSBHDFKGS",
)

dummy_rider = Rider(
    account=dummy_rider_account,
    bikes=[bike_road, bike_fixie]
)

season = Season(
    name="23Z :d",
    start_timestamp=datetime(day=2, month=10, year=2023),
    end_timestamp=datetime(day=19, month=2, year=2024)
)

race1 = Race(
    status=RaceStatus.pending,
    name="Dookoła bloku",
    description="Plan działania:\n"
                "1. Zbiórka (bądźcie proszę na czas! Spóźnialscy gonią peleton)\n"
                "2. Objazd trasy\n"
                "3. Start wyścigu\n"
                "4. Ogłoszenie zwycięzców\n"
                "5. Pamiątkowa fota",
    requirements="Pozytywne nastawienie :))",
    checkpoints_gpx_file="NOT_IMPLEMENTED",
    meetup_timestamp=datetime(day=5, month=12, year=2023, hour=16),
    start_timestamp=datetime(day=5, month=12, year=2023, hour=16, minute=30),
    end_timestamp=datetime(day=5, month=12, year=2023, hour=18),
    entry_fee_gr=1000,
    no_laps=5,
    event_graphic_file="NOT_IMPLEMENTED",
    place_to_points_mapping_json='['
                                 '{"place": 1,"points": 20},'
                                 '{"place": 2,"points": 16},'
                                 '{"place": 3,"points": 12},'
                                 '{"place": 5,"points": 10},'
                                 '{"place": 10,"points": 6},'
                                 '{"place": 999,"points": 4}'
                                 ']',
    sponsor_banners_uuids_json='["NOT_IMPLEMENTED"]',
    season=season,
    bonuses=[],
    race_participations=[]

)

race_bonus_snow = RaceBonus(
    name="Śnieg na trasie",
    rule="NOT_IMPLEMENTED",
    points_multiplier=2.0
)

race2 = Race(
    status=RaceStatus.pending,
    name="Jazda w śniegu",
    description="Jak w tytule. Każdy bierze rower z najgrubszymi oponami jakie ma i "
                "próbujemy nie zagrzebać się w śniegu kręcąc kółka po Polu Mokotowskim. Na mecie przewidziana "
                "ciepła herbatka i kawusia.",
    requirements="Ciepła kurtka i czapka",
    checkpoints_gpx_file="NOT_IMPLEMENTED1",
    meetup_timestamp=datetime(day=20, month=12, year=2023, hour=12),
    start_timestamp=datetime(day=20, month=12, year=2023, hour=12, minute=30),
    end_timestamp=datetime(day=20, month=12, year=2023, hour=14),
    entry_fee_gr=1500,
    no_laps=3,
    temperature=RaceTemperature.cold,
    rain=RaceRain.light,
    event_graphic_file="NOT_IMPLEMENTED1",
    place_to_points_mapping_json='['
                                 '{"place": 1,"points": 20},'
                                 '{"place": 2,"points": 16},'
                                 '{"place": 3,"points": 12},'
                                 '{"place": 5,"points": 10},'
                                 '{"place": 10,"points": 6},'
                                 '{"place": 999,"points": 4}'
                                 ']',
    sponsor_banners_uuids_json='["NOT_IMPLEMENTED1"]',
    season=season,
    bonuses=[race_bonus_snow],
    race_participations=[]
)

race3 = Race(
    status=RaceStatus.ended,
    name="Coffe ride: Pożegnanie lata",
    description="Zgodnie z tradycją 1 października żegnamy sezon letni i wybieramy się do Góry Kawiarni na kawę i "
                "ciacho. Startujemy spod Bikeway na Wilanowie o 12, traska z 60km, po powrocie pizzerka od Sponsora "
                ":)). Charakter trasy raczej będzie sprzyjać rowerom szosowym, ale wytrwałych nie zniechęcamy do "
                "zabrania dowolnego innego sprzętu ;).\nCoffe ride: jedziemy w formule no-drop - nie ścigamy się, "
                "cenne punkty dostajecie za samo wzięcie udziału :D.",
    requirements="Kask!!! Poruszamy się w ruchu drogowym",
    checkpoints_gpx_file="NOT_IMPLEMENTED2",
    meetup_timestamp=datetime(day=1, month=10, year=2023, hour=11, minute=30),
    start_timestamp=datetime(day=1, month=10, year=2023, hour=12, minute=00),
    end_timestamp=datetime(day=1, month=10, year=2023, hour=15),
    entry_fee_gr=0,
    no_laps=1,
    event_graphic_file="NOT_IMPLEMENTED2",
    place_to_points_mapping_json='['
                                 '{"place": 999,"points": 10}'
                                 ']',
    sponsor_banners_uuids_json='["NOT_IMPLEMENTED2"]',
    season=season,
    bonuses=[],
    race_participations=[]

)

dummy_classification = Classification(
    name="Dorośli",
    description=">=18 lat",
    season=season,
)

dummy_rider_classification_link = RiderClassificationLink(
    score=420,
    rider=dummy_rider,
    classification=dummy_classification
)


dummy_race_participation = RaceParticipation(
    status=RaceParticipationStatus.approved.value,
    rider=dummy_rider,
    race=race1,
    bike=bike_road
)

dummy_race_participation_classification_place = RiderParticipationClassificationPlace(
    place=1,
    race_participation=dummy_race_participation,
    classification=dummy_classification
)


initial_data = [
    # dummy_admin_account,
    # dummy_coordinator_account,
    dummy_rider_account,
    # dummy_admin,
    # dummy_coordinator,
    dummy_classification,
    dummy_rider,
    race1,
    race2,
    race3
]
