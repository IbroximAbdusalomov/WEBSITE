# Generated by Django 4.2.2 on 2023-09-21 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('films', '0004_alter_films_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='films',
            name='description',
            field=models.CharField(blank=True, max_length=800, null=True, verbose_name='Описание'),
        ),
    ]
