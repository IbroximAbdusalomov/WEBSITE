# Generated by Django 4.2.2 on 2023-10-17 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('films', '0021_alter_films_top_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='films',
            name='telephone_view_count',
            field=models.PositiveBigIntegerField(default=0, verbose_name='Количество просмотров номер телефона'),
        ),
    ]
