from celery import shared_task

from .models import Products


@shared_task
def decrease_top_duration():
    films = Products.objects.filter(top_duration__gt=0)
    for film in films:
        film.top_duration -= 1
        if film.top_duration < 0:
            film.top_duration = 0
            film.is_top_film = False
        film.save()
