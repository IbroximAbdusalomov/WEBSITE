import asyncio
import emoji
from django.urls import reverse_lazy
from django.views import View
from fuzzywuzzy import fuzz
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import Message, User
from cyrtranslit import to_cyrillic, to_latin
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .utils import send_message_to_channel
from .models import Products, SubCategories, Favorite, Tag
from .forms import FilmsForm, ProductFilterForm, SearchForm, ServiceForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import ListView, CreateView, DetailView, UpdateView


class IndexView(ListView):
    template_name = "index.html"
    context_object_name = "films_buy"

    def get_queryset(self):
        return Products.objects.filter(
            type="buy", is_active=True, is_published=True
        ).order_by("-create_date")[:8]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["films_sell"] = Products.objects.filter(
            type="sell", is_active=True, is_published=True
        ).order_by("-create_date")[:8]
        context["title"] = "Запросы: "
        context["form"] = FilmsForm()
        if self.request.user.is_authenticated:
            in_favorite = list(
                Favorite.objects.filter(user=self.request.user).values_list(
                    "product_id", flat=True
                )
            )
        else:
            in_favorite = []
        context["in_favorite"] = in_favorite
        context["jobs"] = Products.objects.filter(
            is_active=True, is_published=True, category__slug="texnolog"
        )
        return context

    @staticmethod
    def post(request):
        context = {
            "films_buy": Products.objects.filter(
                type="buy", is_active=True, is_published=True
            ).order_by("-create_date")[:8],
            "films_sell": Products.objects.filter(
                type="sell", is_active=True, is_published=True
            ).order_by("-create_date")[:8],
            "title": "Запросы: ",
            # "form": FilmsForm(),
        }
        form = FilmsForm(request.POST)
        selected_tags = request.POST.getlist("tags")
        selected_subcategories = request.POST.getlist("subcategories")
        if form.is_valid():
            film = form.save(commit=False)
            if not request.user.is_anonymous:
                film.author = request.user
                film.email = request.user.email
            film.is_published = True
            film.image = "product-images/image.png"
            if form.cleaned_data["telegram"].startswith("@"):
                film.telegram = form.cleaned_data["telegram"][1:]
            message = {}

            for field_name, field_value in form.cleaned_data.items():
                message[field_name] = field_value
            message["тип"] = "Купить"

            try:
                price = float(form.cleaned_data.get("price", 0))
                film.price = price
            except ValueError:
                film.price = None
            film.save()
            film.sub_category.set(selected_subcategories)
            film.tags.set(selected_tags)
            message["film_id"] = film.id
            asyncio.run(send_message_to_channel(message))
            messages.success(request, "Отправлено на модерацию")
            return redirect("index")
        else:
            context["form"] = form
            context["errors"] = form.errors
            return render(request, "index.html", context=context)


def user_can_view_product(user, film):
    # Проверка, является ли пользователь автором продукта или администратором
    return user == film.author or user.is_staff


class ProductDetailView(DetailView):
    model = Products
    template_name = "product-details.html"
    context_object_name = "product"

    def dispatch(self, request, *args, **kwargs):
        film = self.get_object()

        if not film.is_active:
            if not user_can_view_product(request.user, film):
                return redirect("access_denied_page")
            # Если продукт неактивен, но пользователь - администратор или автор продукта, разрешить доступ
            pass
        session_key = "film_{}_viewed".format(film.pk)

        if not request.session.get(session_key, False):
            film.view_count += 1
            film.save()
            request.session[session_key] = True

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Products.objects.filter(pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        film = self.object
        product_author = Products.objects.get(pk=self.kwargs["pk"]).author
        product_category = Products.objects.get(pk=self.kwargs["pk"]).category_id
        product_sub_category = Products.objects.get(
            pk=self.kwargs["pk"]
        ).sub_category_id

        if not self.request.user.is_anonymous:
            context["is_favorite"] = Favorite.objects.filter(
                user=user, product_id=film
            ).exists()
        context["author_products"] = Products.objects.filter(
            author_id=product_author
        ).order_by("-create_date")[:16]
        similar_products = Products.objects.filter(
            category=product_category, sub_category=product_sub_category
        ).order_by("-create_date")[:16]

        if len(similar_products) < 16:
            add = 16 - len(similar_products)
            additional_products = Products.objects.filter(
                category=product_category
            ).exclude(id__in=[product.id for product in similar_products]).order_by("-create_date")[:add]
            similar_products = list(similar_products) + list(additional_products)

        if len(similar_products) < 16:
            add = 16 - len(similar_products)
            additional_products = Products.objects.filter(
                sub_category=product_sub_category
            ).exclude(id__in=[product.id for product in similar_products]).order_by("-create_date")[:add]
            similar_products = list(similar_products) + list(additional_products)

        context["similar_products"] = similar_products

        return context


class ProductSaveView(CreateView):
    model = Products
    form_class = FilmsForm
    template_name = "form.html"

    def form_valid(self, form):
        film = form.save(commit=False)
        message = {}
        selected_tags = self.request.POST.getlist("tags")
        selected_subcategories = self.request.POST.getlist("subcategories")
        if self.request.POST.get("form-name") == "sell":
            film.type = "sell"
            message["тип"] = "Продать"
            user = self.request.user
            if user.currency >= 10:
                user.currency -= 10
                user.save()
        else:
            film.price = None
            message["тип"] = "Купить"

        film.author = self.request.user if not self.request.user.is_anonymous else None
        if form.cleaned_data["is_price_negotiable"] or not form.cleaned_data["price"]:
            film.price = None

        image = self.request.FILES.get("image")

        if image:
            film.image = image

        film.is_published = True

        for field_name, field_value in form.cleaned_data.items():
            message[field_name] = field_value

        film.save()
        film.sub_category.set(selected_subcategories)
        film.tags.set(selected_tags)

        message["film_id"] = film.id
        if image:
            asyncio.run(send_message_to_channel(message, film.image.path))
        else:
            asyncio.run(send_message_to_channel(message))

        user = self.request.user
        if not user.is_anonymous:
            message = Message.objects.create(
                sender=user,
                message="Вы успешно отправили запрос !.",
                created_at=timezone.now(),
            )

            message.recipients.set([self.request.user])
        messages.success(self.request, "Вы успешно отправили запрос !")

        if self.request.user.is_authenticated:
            return render(self.request, "additional_services.html", {"product": film.pk})
        else:
            return redirect("index")

    def form_invalid(self, form):
        errors = form.errors
        for error in errors:
            messages.error(self.request, f"{errors[f'{error}'][0]}")
        # messages.error(self.request, f'{errors}')
        return render(
            self.request, self.template_name, {"form": form, "errors": errors}
        )


class ProductUpdateStatus(View):
    template_name = "additional_services.html"
    form_class = ServiceForm

    def get(self, request):
        return render(request, self.template_name, {"form": self.form_class()})

    def post(self, request):
        service = self.request.POST.get("service", None)
        product_pk = self.request.POST.get("product", None)
        if service is not None:
            product = Products.objects.get(pk=product_pk)
            if str(service).endswith("1"):
                product.is_top_film = True
                product.top_duration = 1

            elif str(service).endswith("2"):
                product.is_top_film = True
                product.top_duration = 2

            elif str(service).endswith("3"):
                product.is_top_film = True
                product.top_duration = 3
            product.save()
        messages.success(self.request, "Success")
        return redirect("index")


class FilmsUpdateView(UpdateView):
    model = Products
    form_class = FilmsForm
    template_name = "form.html"  # Update with your templates path
    success_url = "/success/"  # Redirect to a success page after updating
    context_object_name = "film"  # Optional: Customize the context object name

    def get_object(self, queryset=None):
        return Products.objects.get(pk=self.kwargs["pk"])


class FilmsListView(ListView):
    model = Products
    template_name = "product-list.html"
    paginate_by = 8
    context_object_name = "films"

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ProductFilterForm(self.request.GET)
        if self.request.user.is_authenticated:
            in_favorite = list(
                Favorite.objects.filter(user=self.request.user).values_list(
                    "product_id", flat=True
                )
            )
        else:
            in_favorite = []
        context["in_favorite"] = in_favorite
        # context['films'] = Films.objects.filter(is_active=True, is_published=True).order_by('-create_date')
        context["top_films"] = Products.objects.filter(
            is_active=True, is_published=True, is_top_film=True
        ).order_by("-create_date")
        # context["companies"] = User.objects.filter(is_business_account=True)
        context["search"] = SearchForm()
        films = Products.objects.filter(is_active=True, is_published=True).order_by(
            "-create_date"
        )
        context["films"] = films

        paginator = Paginator(films, self.paginate_by)
        page = self.request.GET.get("page", 1)

        try:
            films = paginator.page(page)
        except EmptyPage:
            films = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            films = paginator.page(1)

        context["films"] = films
        context["paginator"] = paginator
        return context

    def fuzzywuzzy_search(self, latin_query, cyrillic_query, queryset, threshold):
        similar_products = set()

        latin_words = set(latin_query.split())
        cyrillic_words = set(cyrillic_query.split())

        for product in queryset:
            product_title_words = set(product.title.split())
            product_description_words = set(product.description.split())

            latin_similarity_title = any(
                fuzz.token_set_ratio(word1, word2) >= threshold
                for word1 in product_title_words
                for word2 in latin_words
            )

            cyrillic_similarity_title = any(
                fuzz.token_set_ratio(word1, word2) >= threshold
                for word1 in product_title_words
                for word2 in cyrillic_words
            )

            latin_similarity_description = any(
                fuzz.token_set_ratio(word1, word2) >= threshold
                for word1 in product_description_words
                for word2 in latin_words
            )

            cyrillic_similarity_description = any(
                fuzz.token_set_ratio(word1, word2) >= threshold
                for word1 in product_description_words
                for word2 in cyrillic_words
            )

            if (
                    latin_similarity_title
                    or cyrillic_similarity_title
                    or latin_similarity_description
                    or cyrillic_similarity_description
            ):
                similar_products.add(product)

        return list(similar_products)

    def post(self, request, *args, **kwargs):
        search_form = SearchForm(self.request.POST)
        product_filter_form = ProductFilterForm(self.request.POST)

        if self.request.user.is_authenticated:
            in_favorite = list(
                Favorite.objects.filter(user=self.request.user).values_list(
                    "product_id", flat=True
                )
            )
        else:
            in_favorite = []
        context = {
            "search": SearchForm(),
            "in_favorite": in_favorite,
            "form": ProductFilterForm(),
        }

        # ---------------------------------------------------------------------------------
        queryset = Products.objects.filter(is_active=True, is_published=True)
        companies = User.objects.filter(is_business_account=True)

        if search_form.is_valid():
            query = search_form["query"].data
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
            context["films"] = queryset

        else:
            category = self.request.POST.get("category", "")
            sub_category = self.request.POST.get("sub_category", "")
            tags = self.request.POST.get("tags", "")
            country = self.request.POST.get("country", "")
            city = self.request.POST.get("city", "")
            product_type = self.request.POST.get("type", "")

            if product_type != "company":
                filtered_queryset = new_filter(
                    queryset,
                    companies,
                    category,
                    sub_category,
                    tags,
                    country,
                    city,
                    product_type,
                )
                context["films"] = filtered_queryset

            else:
                filtered_companies = new_filter(
                    queryset,
                    companies,
                    category,
                    sub_category,
                    tags,
                    country,
                    city,
                    product_type,
                )
                context["companies"] = filtered_companies
        return render(request, self.template_name, context=context)


def new_filter(
        queryset,
        companies,
        category="",
        sub_category="",
        tags="",
        country="",
        city="",
        product_type="",
):
    if product_type == "company":
        queryset = companies.all()
    if product_type not in ("all", "company", ""):
        queryset = queryset.filter(type=product_type)
    if category:
        queryset = queryset.filter(category=category)
    if sub_category:
        queryset = queryset.filter(sub_category=sub_category)

    if tags:
        queryset = queryset.filter(tags__in=tags)

    if country:
        queryset = queryset.filter(country=country)

    if city:
        queryset = queryset.filter(city=city)
    return queryset


def related_to_it(request):
    category_id = request.GET.get("category_id", None)
    subcategory_id = request.GET.get("subcategory_id", None)

    sub_categories = {}
    if category_id:
        subcategories = SubCategories.objects.filter(category_id=category_id).all()
        sub_categories = {
            subcategory.id: subcategory.name for subcategory in subcategories
        }

    tags = {}
    if subcategory_id:
        tags_query = Tag.objects.filter(subcategory=subcategory_id)
        tags = {tag.id: tag.name for tag in tags_query}

    return JsonResponse({"subcategories": sub_categories, "tags": tags})


@login_required()
def add_to_favorites(request, pk):
    product = Products.objects.get(pk=pk)
    try:
        favorite = Favorite.objects.get(user=request.user, product_id=product)
        favorite.delete()
        response_data = {"added": False}
    except Favorite.DoesNotExist:
        Favorite.objects.create(user=request.user, product_id=product)
        response_data = {"added": True}
    return JsonResponse(response_data)


def favorite_list(request):
    favorites = {"favorites": Favorite.objects.filter(user=request.user)}
    return JsonResponse(favorites)


def send_message(request, text=None):
    if request.method == "POST" and text:
        messages.error(request, text)
        return JsonResponse({"message": "Message sent successfully"})
    return JsonResponse({"message": "Invalid request"})


def remove_emoji(text):
    return emoji.replace_emoji(text)


def get_suggestions(request):
    # получаю текст из инпута
    user_query = request.GET.get("term", "")
    # текст на латин и кирилицу переожу салом=salom
    latin_query = to_latin(user_query).lower()
    cyrillic_query = to_cyrillic(user_query).lower()
    # latin_products = Products.objects.filter(title__istartswith=latin_query)
    # cyrillic_products = Products.objects.filter(title__istartswith=cyrillic_query)
    all_words = set()

    # добавляю слова в all_worlds
    for product in Products.objects.values("title", "description"):
        title_words = product["title"].split()
        description_words = product["description"].split()
        all_words.update(title_words)
        all_words.update(description_words)

    # удаляю эмации из текста
    all_words = [remove_emoji(word).lower() for word in all_words]

    filtered_words = [
        word
        for word in all_words
        if word.startswith(latin_query) or word.startswith(cyrillic_query)
    ]

    suggestions = filtered_words[:5]

    # это функция для поиска похожего слово
    def find_suggestions(query, limit):
        return [
            word for word in all_words if fuzz.token_set_ratio(word, query) >= limit
        ]

    if len(suggestions) < 5:
        supplement = 5 - len(suggestions)
        filtered_words = [
            word for word in all_words if latin_query in word or cyrillic_query in word
        ]
        suggestions = filtered_words[:supplement]

    for threshold in [90, 80, 70]:
        if len(suggestions) < 5:
            cyrillic_similar_words = find_suggestions(cyrillic_query, threshold)
            latin_similar_words = find_suggestions(latin_query, threshold)

            similar_words = list(set(cyrillic_similar_words + latin_similar_words))

            if similar_words:
                suggestions = similar_words[: 5 - len(suggestions)]
                break

    return JsonResponse(suggestions, safe=False)


def access_denied_page(request):
    return render(request, "access_denied_page.html")


""""""
