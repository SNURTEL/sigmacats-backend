from celery import Celery  # type: ignore
import app.core.celeryconfig as celeryconfig

celery_app = Celery()
celery_app.config_from_object(celeryconfig)
