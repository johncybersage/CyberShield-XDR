from backend.workers.celery_app import celery_app


@celery_app.task(name="backend.workers.notification_tasks.send_notification")
def send_notification(notification_id: str):
    pass
