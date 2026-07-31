"""
CyberShield XDR — Celery Application
Async task queue for long-running operations:
- Vulnerability scans (can take minutes)
- Malware analysis
- Report generation
- Threat intel enrichment
- Notification delivery

Separate queues allow independent scaling of worker types.
"""
from celery import Celery

from backend.config.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "cybershield",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "backend.workers.scan_tasks",
        "backend.workers.malware_tasks",
        "backend.workers.report_tasks",
        "backend.workers.notification_tasks",
        "backend.workers.threat_intel_tasks",
    ],
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Reliability
    task_acks_late=True,           # Acknowledge after completion, not on receipt
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,  # One task at a time per worker (fair dispatch)

    # Result expiry
    result_expires=86400,          # 24 hours

    # Task routing — separate queues for different workloads
    task_routes={
        "backend.workers.scan_tasks.*": {"queue": "scans"},
        "backend.workers.malware_tasks.*": {"queue": "malware"},
        "backend.workers.report_tasks.*": {"queue": "reports"},
        "backend.workers.notification_tasks.*": {"queue": "notifications"},
        "backend.workers.threat_intel_tasks.*": {"queue": "threat_intel"},
    },

    # Beat schedule for periodic tasks
    beat_schedule={
        "refresh-threat-intel-daily": {
            "task": "backend.workers.threat_intel_tasks.refresh_threat_feeds",
            "schedule": 86400.0,  # Every 24 hours
        },
        "cleanup-old-scans": {
            "task": "backend.workers.scan_tasks.cleanup_old_scans",
            "schedule": 3600.0,   # Every hour
        },
    },
)
