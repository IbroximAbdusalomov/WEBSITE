from django.contrib.auth.models import AbstractUser
from django.db.models import Avg, PositiveIntegerField
from django.db.models import Model, CharField, ImageField, EmailField, BooleanField, ForeignKey, SET_NULL, \
    ManyToManyField, CASCADE, TextField, DateTimeField, IntegerField

from films.models import Categories, SubCategories, Tag, Country


class User(AbstractUser):
    telephone = CharField(max_length=50, null=True, blank=True)
    email = EmailField(unique=True)
    trust = BooleanField(default=False)
    profile_photo = ImageField(upload_to='profile_photos/', default='static/default-logo.svg')
    company_name = CharField(max_length=100, blank=True, null=True)
    category = ForeignKey(Categories, SET_NULL, blank=True, null=True, related_name='user_category')
    sub_category = ForeignKey(SubCategories, SET_NULL, blank=True, null=True, related_name='user_sub_category')
    tags = ManyToManyField(Tag, blank=True)
    telegram = CharField(max_length=100, blank=True, null=True)
    whatsapp = CharField(max_length=100, blank=True, null=True)
    website = CharField(max_length=500, blank=True, null=True)
    url_maps = CharField(max_length=500, blank=True, null=True)
    banner = ImageField(upload_to='company_banners/', blank=True, null=True)
    logo = ImageField(upload_to='company_logos/', blank=True, null=True)
    description = CharField(max_length=1000, blank=True, null=True)
    country = ForeignKey(Country, SET_NULL, blank=True, null=True)
    is_business_account = BooleanField(default=False, null=True)
    ball = IntegerField(default=100)

    def __str__(self):
        return self.username

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def calculate_average_rating(self):
        return UserRating.objects.filter(rated_user=self).aggregate(Avg('rating'))['rating__avg'] or 0


class Message(Model):
    sender = ForeignKey(User, on_delete=CASCADE, related_name='sent_messages')
    recipients = ManyToManyField(User, related_name='received_messages')
    message = TextField()
    created_at = DateTimeField(auto_now_add=True)
    is_read = BooleanField(default=False)

    def __str__(self):
        recipients_str = ', '.join(str(user) for user in self.recipients.all())
        return f"Message from {self.sender} to {recipients_str}: {self.message}"


class UserRating(Model):
    rater = ForeignKey(User, related_name='ratings_given', on_delete=CASCADE)
    rated_user = ForeignKey(User, related_name='ratings_received', on_delete=CASCADE)
    rating = PositiveIntegerField()

    class Meta:
        unique_together = (('rater', 'rated_user'),)

    def __str__(self):
        return f"Rating from {self.rater} to {self.rated_user}: {self.rating}"
