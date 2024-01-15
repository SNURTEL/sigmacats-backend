import shutil

from fastapi import Depends, Request, APIRouter

from starlette.datastructures import FormData
from sqlmodel import Session
from sqlmodel import select

from app.util.log import get_logger
from app.db.session import get_db
from app.tasks import basic_tasks

from app.models.account import Account

logger = get_logger()

router = APIRouter()

"""
This file contains basic tests for database and celery to ensure proper operation
"""


@router.get("/celery")
async def celery_test() -> dict[str, str]:
    """
    Test celery setup
    """
    r = basic_tasks.test_celery.delay()
    return {"Queued task": f"{r}"}


@router.get("/db")
async def db_test(db: Session = Depends(get_db)) -> list[Account]:
    """
    Test database read
    """
    accounts = db.exec(select(Account)).all()
    logger.info(accounts)
    return accounts  # type: ignore[return-value]


@router.post("/upload-test/")
async def upload_test(request: Request) -> dict[str, str]:
    """
    Test database write
    """
    form: FormData = await request.form()
    filename = str(form.get('fileobj.path'))
    with open(filename, mode='r', encoding='utf-8') as fp:
        print(fp.read(512))
    shutil.copy2(filename, '/attachments/' + filename.split('/')[-1])

    return {  # type: ignore[return-value]
        k: form.get(k) for k in (  # type: ignore[misc]
            'fileobj.name',
            'fileobj.content_type',
            'fileobj.path',
            'fileobj.md5',
            'fileobj.size',
            'name')
    }
