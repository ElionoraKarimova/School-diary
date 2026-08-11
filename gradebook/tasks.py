import logging
from celery import shared_task
logger = logging.getLogger("gradebook")

@shared_task
def notify_grade_created(grade_id):
    from .models import Grade
    try:
        grade = Grade.objects.select_related("student", "subject").get(pk=grade_id)
    except Grade.DoesNotExist:
        logger.info("notify_grade_created: grade %s no longer exists", grade_id)
        return "skipped: grade missing"

    logger.info(
        "Notification: %s received %s in %s",
        grade.student.username,
        grade.value,
        grade.subject.name,
    )
    return f"notified for grade {grade_id}"