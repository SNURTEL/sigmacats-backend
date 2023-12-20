import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router


app_name = os.getenv("FASTAPI_APP_NAME", "NAME NOT SET")
api_prefix = os.getenv("FASTAPI_API_PREFIX", "/api")


app = FastAPI(
    title=app_name,
    openapi_url=f"{api_prefix}/openapi.json",
    docs_url=f"{api_prefix}/docs",
    redoc_url=f"{api_prefix}/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=api_prefix)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}
