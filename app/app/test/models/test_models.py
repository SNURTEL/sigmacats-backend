from sqlmodel import select

from app.models.bike import Bike
from app.models.account import Account
from app.models.rider import Rider


def test_key_increment(db) -> None:  # type: ignore[no-untyped-def]
    account = Account(
        username="testuser",
        type="rider",
        name="test",
        surname="user",
        email="test@user.com",
        hashed_password="JYGFJYGFTUJY"
    )

    bike1 = Bike(name="bike1", type="road")
    bike2 = Bike(name="bike2", type="road")

    rider = Rider(
        account=account,
        bikes=[bike1, bike2]
    )

    db.add(rider)

    db.commit()
    with db:
        statement = select(Bike).where(Bike.id > 10000)  # type: ignore[operator, var-annotated]
        result = db.exec(statement)
        bikes = result.all()
        assert bikes[0].id == 10001
        assert bikes[1].id == 10002
