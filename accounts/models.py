from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, ImageField, EmailField, TextField, BooleanField


class User(AbstractUser):
    telephone = CharField(max_length=50, null=True, blank=True)
    email = EmailField(unique=True)
    trust = BooleanField(default=False)

    # Остальные поля пользователя, которые ранее были в модели Company
    description = TextField(blank=True, null=True)  # Описание компании
    banner = ImageField(upload_to='company_banners/', blank=True)
    logo = ImageField(upload_to='company_logos/', default='static/default-logo.svg')
    category = CharField(max_length=100, blank=True)  # Замените на поле, которое представляет категорию
    subcategory = CharField(max_length=100, blank=True)  # Замените на поле, которое представляет подкатегорию
    telegram = CharField(max_length=100, blank=True)
    whatsapp = CharField(max_length=100, blank=True)
    country = CharField(max_length=100, blank=True)  # Добавлено поле для страны
    is_business_account = BooleanField(default=False)

    def __str__(self):
        return self.username

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
