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


@router.get("/celery")
async def celery_test() -> dict[str, str]:
    r = basic_tasks.test_celery.delay()
    return {"Queued task": f"{r}"}


@router.get("/db")
async def db_test(db: Session = Depends(get_db)) -> list[Account]:
    accounts = db.exec(select(Account)).all()
    logger.info(accounts)
    return accounts  # type: ignore[return-value]


@router.post("/upload-test/")
async def upload_test(request: Request) -> dict[str, str]:
    form: FormData = await request.form()
    return {
        k: form.get(k) for k in (  # type: ignore[misc]
            'fileobj.name',
            'fileobj.content_type',
            'fileobj.path',
            'fileobj.md5',
            'fileobj.size',
            'name')
    }
