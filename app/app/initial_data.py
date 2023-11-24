from app.models.account import Account

dummy_account = Account(
    type="admin",
    username="dummy_admin",
    name="John",
    surname="Doe",
    email="j.doe@sigma.org",
    password_hash="JSDHFGKIUSDFHBKGSBHDFKGS"
)

initial_data = [
    dummy_account
]
