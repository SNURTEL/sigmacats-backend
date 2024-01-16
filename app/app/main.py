import os

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.api.api import api_router
from app.util.log import get_logger

"""
Main app file
"""

logger = get_logger()

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
    allow_origins=[os.environ.get("FRONTEND_URL", "localhost")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD", "OPTIONS", "PATCH", "DELETE"],
    allow_headers=["Access-Control-Allow-Headers", 'Content-Type', 'Authorization', 'Access-Control-Allow-Origin'],
)

app.include_router(api_router, prefix=api_prefix)
