import os

from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy, CookieTransport


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
cookie_transport = CookieTransport(cookie_max_age=3600)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=str(os.environ.get("FASTAPI_JWT_SECRET")),
                       lifetime_seconds=3600)


jwt_auth_backend = AuthenticationBackend(
    name="bearer",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
cookie_auth_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
