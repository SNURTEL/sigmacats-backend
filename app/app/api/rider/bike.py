from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from app.db.session import get_db

from app.models.bike import Bike, BikeCreate, BikeUpdate
from app.models.rider import Rider

router = APIRouter()


# mypy: disable-error-code=var-annotated

@router.get("/")
async def read_bikes(
        rider_id: int,  # TODO deduce from session,
        limit: int = 30, offset: int = 0,
        db: Session = Depends(get_db)
) -> list[Bike]:
    """
    List all bikes owned by a given rider.
    """
    stmt = (
        select(Bike)
        .where(Bike.rider_id == rider_id)
        .offset(offset)
        .limit(limit)
        .order_by(Bike.id)  # type: ignore[arg-type]
    )
    bikes = db.exec(stmt).all()

    return bikes  # type: ignore[return-value]


@router.get("/{id}")
async def read_bike(
        id: int,
        rider_id: int,  # TODO deduce from session
        db: Session = Depends(get_db),
) -> Bike:
    """
    Get details about a specific bike.
    """
    stmt = (
        select(Bike)
        .where(Bike.id == id, Bike.rider_id == rider_id)
    )
    bike = db.exec(stmt).first()

    if not bike:
        raise HTTPException(404)

    return bike


@router.post("/create")
async def create_bike(
        bike_create: BikeCreate,
        db: Session = Depends(get_db),
) -> Bike:
    """
    Create a new bike.
    """
    if db.exec(select(Bike).where(
            Bike.name == bike_create.name,
            Bike.type == bike_create.type,
            Bike.brand == bike_create.brand,
            Bike.model == bike_create.model)).first():
        raise HTTPException(403, "Identical bike already exists")

    if not db.get(Rider, bike_create.rider_id):
        raise HTTPException(404, "Rider not found")

    try:
        bike = Bike.from_orm(bike_create)
        db.add(bike)
        db.commit()
    except (IntegrityError, ValidationError):
        raise HTTPException(400)

    return bike


@router.patch("/{id}")
async def update_bike(
        id: int,
        rider_id: int,  # TODO deduce from session
        bike_update: BikeUpdate,
        db: Session = Depends(get_db)
) -> Bike:
    """
    Update bike details.
    """
    stmt = (
        select(Bike)
        .where(Bike.id == id, Bike.rider_id == rider_id)
    )
    bike = db.exec(stmt).first()

    if not bike:
        raise HTTPException(404)

    try:
        bike_data = bike_update.dict(exclude_unset=True, exclude_defaults=True)
        for k, v in bike_data.items():
            setattr(bike, k, v)
        db.add(bike)
        db.commit()
        db.refresh(bike)
    except (IntegrityError, ValidationError):
        raise HTTPException(400)

    return bike
