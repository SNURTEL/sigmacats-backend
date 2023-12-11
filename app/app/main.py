import os

from fastapi import FastAPI, Depends, Request
from starlette.datastructures import FormData
from sqlmodel import Session
from sqlmodel import select

from app.util.log import get_logger
from app.db.session import get_db
from app.tasks import basic_tasks
from app.api.api import api_router

from app.models.account import Account

logger = get_logger()

app_name = os.getenv("FASTAPI_APP_NAME", "NAME NOT SET")
api_prefix = os.getenv("FASTAPI_API_PREFIX", "/api")

app = FastAPI(
    title=app_name, openapi_url=f"{api_prefix}/openapi.json"
)

app.include_router(api_router, prefix=api_prefix)


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
    return accounts  # type: ignore[return-value]


@app.post("/upload-test/")
async def upload_test(request: Request) -> dict[str, str]:
    logger.info(request.headers)
    form: FormData = await request.form()
    logger.info(form)
    return {
        k: form.get(k) for k in (  # type: ignore[misc]
            'fileobj.name',
            'fileobj.content_type',
            'fileobj.path',
            'fileobj.md5',
            'fileobj.size',
            'name')
    }
