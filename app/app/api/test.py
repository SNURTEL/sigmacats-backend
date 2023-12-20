import shutil

from fastapi import Depends, Request, APIRouter

from starlette.datastructures import FormData
from sqlmodel import Session
from sqlmodel import select

from app.util.log import get_logger
from app.db.session import get_db
from app.tasks import basic_tasks

from app.models.account import Account
from app.core.users import current_active_user, current_rider_user, current_coordinator_user

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


@router.get("/protected")
async def protected(user: Account = Depends(current_active_user)) -> dict[str, str]:
    return {'message': 'you have successfully accessed a protected endpoint'}  # type: ignore[return-value]


@router.get("/protected-rider")
async def protected_rider(user: Account = Depends(current_rider_user)) -> dict[str, str]:
    return {'message': 'this is a rider-only endpoint'}  # type: ignore[return-value]


@router.get("/protected-coordinator")
async def protected_rider(user: Account = Depends(current_coordinator_user)) -> dict[str, str]:
    return {'message': 'this is a coordinator-only endpoint'}  # type: ignore[return-value]