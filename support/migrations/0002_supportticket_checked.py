# Generated by Django 4.2.7 on 2024-01-11 12:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("support", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="supportticket",
            name="checked",
            field=models.BooleanField(default=False),
        ),
    ]
