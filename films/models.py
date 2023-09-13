from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, CharField, SlugField, CASCADE, ForeignKey, TextField, DateTimeField, BooleanField, \
    PositiveBigIntegerField, ImageField, SET_NULL, FloatField, ManyToManyField, IntegerField
from django.urls import reverse_lazy


class Categories(Model):
    slug = SlugField(unique=True)
    name = CharField("Категория", max_length=50)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy("category_detail", kwargs={
            "slug": self.slug
        })

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class SubCategories(Model):
    slug = SlugField(unique=True)
    category = ForeignKey(Categories, on_delete=CASCADE)
    name = CharField("Субкатегория", max_length=100)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy("subcategory_detail", kwargs={
            "slug": self.slug
        })

    class Meta:
        verbose_name = "Субкатегория"
        verbose_name_plural = "Субкатегории"


class Country(Model):
    slug = SlugField(unique=True)
    name = CharField("Страна", max_length=50)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy("country_detail", kwargs={
            "slug": self.slug
        })

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страна"


class City(Model):
    slug = SlugField(unique=True)
    country = ForeignKey(Country, on_delete=CASCADE)
    name = CharField("Город", max_length=100)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy("city_detail", kwargs={
            "slug": self.slug
        })

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Город"


class Tag(Model):
    name = CharField(max_length=255, unique=True)
    category = ForeignKey(Categories, on_delete=CASCADE, blank=True, null=True, related_name='tags')
    subcategory = ForeignKey(SubCategories, on_delete=CASCADE, blank=True, null=True, related_name='tags')

    def __str__(self):
        return self.name


class Films(Model):  # Модель

    TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    title = CharField("Наименование", max_length=100)
    description = TextField("Описание", null=True, blank=True)
    telephone = CharField("Номер телефона", max_length=30)
    email = CharField("Емайл адрес", max_length=100)
    image = ImageField("Картинка", upload_to="product-images/", blank=True, null=True)
    view_count = PositiveBigIntegerField("Количество просмотров", default=0)
    create_date = DateTimeField("Дата создания", auto_now_add=True)
    update_date = DateTimeField("Дата обновления", auto_now=True)
    is_published = BooleanField("Опубликовано", default=True)
    country = ForeignKey(Country, on_delete=CASCADE)
    city = ForeignKey(City, on_delete=CASCADE, blank=True, null=True)
    category = ForeignKey(Categories, CASCADE)
    sub_category = ForeignKey(SubCategories, CASCADE)
    tags = ManyToManyField(Tag, blank=True)
    is_active = BooleanField(default=False)
    type = CharField(max_length=50, choices=TYPE_CHOICES, default='buy')
    author = ForeignKey(get_user_model(), SET_NULL, blank=True, null=True)
    price = FloatField("Цена", blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy("film_detail", kwargs={
            "pk": self.pk
        })

    class Meta:
        verbose_name = "Запрос"
        verbose_name_plural = "Запросы"


class Favorite(Model):
    user = ForeignKey(get_user_model(), CASCADE)
    product_id = ForeignKey(Films, CASCADE)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product_id')

    def __str__(self):
        return f"{self.user} - Product ID: {self.product_id}"


class Rating(Model):
    user = ForeignKey(get_user_model(), on_delete=CASCADE)
    product = ForeignKey(Films, on_delete=CASCADE, default=None)
    stars = IntegerField("Оценка", default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} - Product: {self.product} - Stars: {self.stars}"
