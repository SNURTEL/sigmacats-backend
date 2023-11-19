import os

broker_url = os.environ.get("CELERY_BROKER_URL")
result_backend = os.environ.get("CELERY_RESULT_BACKEND_URL")
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
imports = ('app.tasks.basic_tasks', )
