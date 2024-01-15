import os
import logging
from logging.config import dictConfig

from pydantic import BaseModel

LOG_TAG = os.environ.get("FASTAPI_LOG_TAG", default="=== NO LOG TAG SET ===")

"""
This file contains functionalities for logging the execution of the application
"""

class LogConfig(BaseModel):
    """
    Class for logging the execution of the application
    """
    LOGGER_NAME: str = LOG_TAG
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }


dictConfig(LogConfig().dict())


def get_logger() -> logging.Logger:
    """
    Function for getting a logger
    """
    return logging.getLogger(LOG_TAG)
