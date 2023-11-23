from sqlmodel import select

from app.models.bike import Bike


def test_key_increment(db) -> None:  # type: ignore[no-untyped-def]
    bike1 = Bike(name="bike1", type="road")
    bike2 = Bike(name="bike2", type="road")
    db.add(bike1)
    db.add(bike2)
    db.commit()
    with db:
        statement = select(Bike)
        result = db.execute(statement)
        bikes = result.all()[0]
        assert bikes[0].id == 1
        assert bikes[1].id == 2