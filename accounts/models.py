from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg, PositiveIntegerField
from django.db.models import (
    Model,
    CharField,
    ImageField,
    EmailField,
    BooleanField,
    ForeignKey,
    SET_NULL,
    ManyToManyField,
    CASCADE,
    TextField,
    DateTimeField,
    IntegerField,
    DecimalField,
)

from films.models import Categories, SubCategories, Tag, Country


class User(AbstractUser):
    telephone = CharField(max_length=50, null=True, blank=True)
    email = EmailField(unique=True)
    trust = BooleanField(default=False)
    profile_photo = ImageField(
        upload_to="profile_photos/", default="static/default-logo.svg"
    )
    company_name = CharField(max_length=100, blank=True, null=True)
    category = ForeignKey(
        Categories, SET_NULL, blank=True, null=True, related_name="user_category"
    )
    sub_category = ForeignKey(
        SubCategories, SET_NULL, blank=True, null=True, related_name="user_sub_category"
    )
    tags = ManyToManyField(Tag, blank=True)
    telegram = CharField(max_length=100, blank=True, null=True)
    whatsapp = CharField(max_length=100, blank=True, null=True)
    website = CharField(max_length=500, blank=True, null=True)
    url_maps = CharField(max_length=500, blank=True, null=True)
    banner = ImageField(upload_to="company_banners/", blank=True, null=True)
    logo = ImageField(upload_to="company_logos/", blank=True, null=True)
    description = CharField(max_length=1000, blank=True, null=True)
    country = ForeignKey(Country, SET_NULL, blank=True, null=True)
    is_business_account = BooleanField(default=None, null=True)
    currency = DecimalField(max_digits=10, decimal_places=3, default=100.000)
    previous_currency = DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)

    def __str__(self):
        return self.username

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

    def calculate_average_rating(self):
        return (
                UserRating.objects.filter(rated_user=self).aggregate(Avg("rating"))[
                    "rating__avg"
                ]
                or 0
        )

    def save(self, *args, **kwargs):
        if self.pk:
            # Если у пользователя уже есть первичный ключ, это обновление
            self.previous_currency = self._get_previous_value("currency", self.currency)
        super().save(*args, **kwargs)

    def _get_previous_value(self, field_name, current_value):
        # Метод для получения предыдущего значения поля
        if self.pk:
            previous_instance = self.__class__._default_manager.get(pk=self.pk)
            return getattr(previous_instance, field_name)
        return current_value


class Message(Model):
    sender = ForeignKey(User, on_delete=CASCADE, related_name="sent_messages")
    recipients = ManyToManyField(User, related_name="received_messages")
    message = TextField()
    created_at = DateTimeField(auto_now_add=True)
    is_read = BooleanField(default=False)

    def __str__(self):
        recipients_str = ", ".join(str(user) for user in self.recipients.all())
        return f"Message from {self.sender} to {recipients_str}: {self.message}"


class UserRating(Model):
    rater = ForeignKey(User, related_name="ratings_given", on_delete=CASCADE)
    rated_user = ForeignKey(User, related_name="ratings_received", on_delete=CASCADE)
    rating = PositiveIntegerField()

    class Meta:
        unique_together = (("rater", "rated_user"),)

    def __str__(self):
        return f"Rating from {self.rater} to {self.rated_user}: {self.rating}"


class UserSubscription(Model):
    subscriber = ForeignKey(
        get_user_model(), on_delete=CASCADE, related_name="subscriptions"
    )
    target_user = ForeignKey(
        get_user_model(), on_delete=CASCADE, related_name="subscribers"
    )
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("subscriber", "target_user")

    def __str__(self):
        return f"{self.subscriber} подписан на {self.target_user}"


class Complaint(Model):
    COMPLAINT_CHOICES = [
        ("spam", "Спам"),
        ("inappropriate_content", "Неуместный контент"),
        ("harassment", "Домогательство"),
        # Добавьте другие варианты по вашему усмотрению
    ]

    complaint_type = CharField(
        max_length=50, choices=COMPLAINT_CHOICES, verbose_name="Тип жалобы"
    )

    description = TextField(verbose_name="Описание проблемы")

    sender = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="sent_complaints",
        verbose_name="Отправитель",
    )

    recipient = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="received_complaints",
        verbose_name="Получатель",
    )

    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.complaint_type} - {self.sender.username} to {self.recipient.username} - {self.created_at}"


class PointsTransaction(Model):
    TRANSACTION_TYPES = (
        ("purchase", "Purchase"),
        ("usage", "Usage"),
    )

    user = ForeignKey(User, on_delete=CASCADE)
    transaction_type = CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = PositiveIntegerField()
    timestamp = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"


@receiver(post_save, sender=get_user_model())
def update_ball_transaction(sender, instance, created, **kwargs):
    if not created:
        previous_ball = instance.previous_ball

        PointsTransaction.objects.create(
            user=instance,
            transaction_type="purchase" if instance.ball > previous_ball else "usage",
            amount=abs(instance.ball - previous_ball),
        )
