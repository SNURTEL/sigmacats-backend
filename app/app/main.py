from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.tasks import basic_tasks

app = FastAPI()


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.get("/celery")
async def celery_test() -> dict[str, str]:
    r = basic_tasks.test_celery.delay()
    return {"Queued task": f"{r}"}


@app.get("/db")
async def db_test(db: Session = Depends(get_db)) -> dict[str, str]:
    result = db.execute("SELECT table_name FROM all_tables").all()  # type: ignore
    return {"tables": str(result)}
