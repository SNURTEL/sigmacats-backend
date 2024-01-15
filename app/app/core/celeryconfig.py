import os

"""
This file contains configuration fo celery, distributed task queue
"""

broker_url = os.environ.get("CELERY_BROKER_URL")
result_backend = os.environ.get("CELERY_RESULT_BACKEND_URL")
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
imports = (
    'app.tasks.basic_tasks',
    'app.tasks.process_race_result_submission',
    'app.tasks.generate_race_places',
    'app.tasks.assign_places_in_classifications',
    'app.tasks.recalculate_classification_scores',
    'app.tasks.set_race_in_progress',
)
