# Generated by Django 4.2.2 on 2023-10-28 18:16

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('films', '0027_categories_is_linked'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Films',
            new_name='Products',
        ),
    ]
