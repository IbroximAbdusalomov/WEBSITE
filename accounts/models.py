from django.contrib.auth.models import AbstractUser
from django.db.models import EmailField, IntegerField, CharField, BooleanField
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):
    telephone = CharField(max_length=50)
    email = EmailField(unique=True)
    score = IntegerField(default=50, validators=[
        # MaxValueValidator(50),
        MinValueValidator(0)
    ])
    trust = BooleanField(default=False)

    # favorites =

    # code = CharField(max_length=4, blank=True, null=True)

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
