from sqlmodel import select

from app.models.dummy import Dummy


def test_db_connection(db) -> None:  # type: ignore[no-untyped-def]
    dummy = Dummy(id=1, foo="bar")
    db.add(dummy)
    db.commit()
    with db:
        statement = select(Dummy)
        result = db.execute(statement)
        dummies = result.all()
        assert dummies == [(dummy,)]
