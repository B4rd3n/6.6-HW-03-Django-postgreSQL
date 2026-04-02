import logging
import os
from dotenv import load_dotenv
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta


from ...models import Post, Subscriber

load_dotenv()

logger = logging.getLogger(__name__)


# наша задача по выводу текста на экран
def my_job():


    today = timezone.now()
    frequency = 7
    first_day = today - timedelta(days=frequency)
    posts_list = Post.objects.filter(creation_time__range=[first_day, today])

    if not posts_list.exists():
        return

    for user in User.objects.all():
        print(user)
        user_categories = Subscriber.objects.filter(user_sub=user).values_list('category', flat=True)
        posts_for_user = posts_list.filter(post_category__in=user_categories).distinct()

        if posts_for_user.exists():

            html_content = render_to_string(
                'weekly_mail.html',
                {
                    'post_list': posts_for_user,
                    'user': user,
                }
            )

            msg = EmailMultiAlternatives(
                subject=f'Привет',
                body='Test django',
                from_email=os.getenv('EMAIL_HOST_USER'),
                to=[user.email],
            )
            msg.attach_alternative(html_content, "text/html")


            try:
                msg.send()
                print(f"Отправлено пользователю: {user.email}")
            except Exception as e:
                print(f"Ошибка при отправке {user.email}: {e}")



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
            trigger=CronTrigger(day="*/7"),
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