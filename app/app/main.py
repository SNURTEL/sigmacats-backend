from fastapi import FastAPI, Depends
from sqlmodel import Session
from sqlmodel import select

from app.util.log import get_logger
from app.db.session import get_db
from app.tasks import basic_tasks

from app.models.account import Account


app = FastAPI()

logger = get_logger()

@app.get("/")
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.get("/celery")
async def celery_test() -> dict[str, str]:
    r = basic_tasks.test_celery.delay()
    return {"Queued task": f"{r}"}


@app.get("/db")
async def db_test(db: Session = Depends(get_db)) -> list[Account]:
    accounts = db.exec(select(Account)).all()
    logger.info(accounts)
    return accounts
