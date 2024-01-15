from celery import Celery  # type: ignore
import app.core.celeryconfig as celeryconfig

"""
This file sets up celery, tool for task queue
"""

celery_app = Celery()
celery_app.config_from_object(celeryconfig)
