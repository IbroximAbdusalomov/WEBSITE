from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from elasticsearch_dsl import Document, Text, Integer
from elasticsearch_dsl.connections import connections

from .models import Products

connections.create_connection()


class FilmsIndex(Document):
    title = Text()
    description = Text()
    category = Integer()

    class Index:
        name = 'films'


FilmsIndex.init()


@receiver(post_save, sender=Products)
def index_films(sender, instance, **kwargs):
    instance.indexing()


@receiver(post_delete, sender=Products)
def delete_films(sender, instance, **kwargs):
    instance.unindexing()
