import pytest
import itertools
from datetime import datetime

from fastapi.encoders import jsonable_encoder

from app.models.account import Account, AccountType, AccountCreate, Gender


# most account-management logic exists in the library, we are going to test only a small subset of overall functionality


@pytest.mark.parametrize("client,code",
                         [
                             (pytest.lazy_fixture("client_unauthenticated"), 401),
                             (pytest.lazy_fixture("rider1_client"), 200),
                             (pytest.lazy_fixture("coordinator_client"), 403),
                             (pytest.lazy_fixture("admin_client"), 403)
                         ])
def test_accounts_rider_api_access(client, code):
    response = client.get("/api/rider/race")
    assert response.status_code == code


@pytest.mark.parametrize("client,code",
                         [
                             (pytest.lazy_fixture("client_unauthenticated"), 401),
                             (pytest.lazy_fixture("rider1_client"), 403),
                             (pytest.lazy_fixture("coordinator_client"), 200),
                             (pytest.lazy_fixture("admin_client"), 403)
                         ])
def test_accounts_coordinator_api_access(client, code):
    response = client.get("/api/coordinator/race")
    assert response.status_code == code


def test_accounts_create_rider_account_200(client_unauthenticated, db):
    ac = AccountCreate(
        type=AccountType.rider,
        email="testuser123@sigma.org",
        password="qwerty123",
        username="testuser",
        name="test",
        surname="users",
        gender=Gender.female,
        birth_date=datetime.now()
    )
    response = client_unauthenticated.post(
        '/api/auth/register', json=jsonable_encoder(ac)
    )
    assert response.status_code == 201
    assert all(response.json().get(k) == jsonable_encoder(ac).get(k) for k in ["name", "surname", "email", "type"])
    account_id = int(response.json().get("id"))
    db_account = db.get(Account, account_id)
    assert db_account.rider.id == account_id


@pytest.mark.parametrize("type",
                         [
                             AccountType.coordinator,
                             AccountType.coordinator,
                         ])
def test_accounts_create_staff_unauthorized_401(type, client_unauthenticated):
    ac = AccountCreate(
        type=type,
        email="testuser123@sigma.org",
        password="qwerty123",
        username="testuser",
        name="test",
        surname="users",
        gender=Gender.female,
        birth_date=datetime.now(),
        phone_number="+48123456789"
    )
    response = client_unauthenticated.post(
        '/api/auth/register', json=jsonable_encoder(ac)
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    "client,type",
    list(itertools.product(
        (
                pytest.lazy_fixture("rider1_client"),
                pytest.lazy_fixture("coordinator_client"),
                pytest.lazy_fixture("admin_client")
        ),
        (
                AccountType.coordinator,
                AccountType.admin,
        )
    )))
def test_accounts_create_staff_account_307(client, type):
    ac = AccountCreate(
        type=type,
        email="testuser123@sigma.org",
        password="qwerty123",
        username="testuser",
        name="test",
        surname="users",
        gender=Gender.female,
        birth_date=datetime.now(),
        phone_number="+48123456789"
    )
    response = client.post(
        '/api/auth/register', json=jsonable_encoder(ac), follow_redirects=False
    )
    assert response.status_code == 307
    assert response.headers['location'].endswith("/api/auth/register/staff")


@pytest.mark.parametrize(
    "client,type",
    list(itertools.product(
        (
                pytest.lazy_fixture("rider1_client"),
                pytest.lazy_fixture("coordinator_client")
        ),
        (
                AccountType.coordinator,
                AccountType.admin,
        )
    )))
def test_accounts_create_staff_account_403(client, type):
    ac = AccountCreate(
        type=type,
        email="testuser123@sigma.org",
        password="qwerty123",
        username="testuser",
        name="test",
        surname="users",
        gender=Gender.female,
        birth_date=datetime.now(),
        phone_number="+48123456789"
    )
    response = client.post(
        '/api/auth/register/staff', json=jsonable_encoder(ac)
    )
    assert response.status_code == 403


@pytest.mark.parametrize(
    "type",
    [
        AccountType.coordinator,
        AccountType.admin,
    ])
def test_accounts_create_staff_account_as_admin_200(type, admin_client, db):
    ac = AccountCreate(
        type=type,
        email="testuser123@sigma.org",
        password="qwerty123",
        username="testuser",
        name="test",
        surname="users",
        gender=Gender.female,
        birth_date=datetime.now(),
        phone_number="+48123456789"
    )
    response = admin_client.post(
        '/api/auth/register/staff', json=jsonable_encoder(ac)
    )
    assert response.status_code == 201
    assert all(response.json().get(k) == jsonable_encoder(ac).get(k) for k in ["name", "surname", "email", "type"])
    account_id = int(response.json().get("id"))
    db_account = db.get(Account, account_id)
    if type == AccountType.coordinator:
        assert db_account.coordinator.id == account_id
    else:
        assert db_account.admin.id == account_id
