import logging
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from BulletinBoard.models import Post, OneTimeCode
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


# наша задача по выводу текста на экран
def my_job():
    print('-----------------------------')
    some_day_last_week = timezone.now().date() - timedelta(days=7)
    OneTimeCode.objects.all().delete()
    User.objects.filter(Q(date_joined__lt=some_day_last_week) & Q(is_active=False)).delete()
    posts = Post.objects.filter(created__gt=some_day_last_week)
    post_list = []
    email_list = []
    for post in posts:
        post_list.append(post.title)
    users = User.objects.all()
    for user in users:
        if user.groups.filter(name='subscribe').exists():
            email_list.append(user.email)

    send_mail(
        subject='Список новых статей, появившийся за неделю!',
        message="\n".join(post_list),
        from_email='snewsportal@yandex.by',
        recipient_list=email_list
    )


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="mon", hour="08", minute="00"),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")