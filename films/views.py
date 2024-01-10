import emoji
import asyncio
from fuzzywuzzy import fuzz
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import Message, User
from .utils import send_message_to_channel
from cyrtranslit import to_cyrillic, to_latin
from django.shortcuts import redirect, render
from django.db.models import CharField, Case, Value, When
from django.contrib.auth.decorators import login_required
from .models import Products, SubCategories, Favorite, Tag
from .forms import FilmsForm, ProductFilterForm, SearchForm
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

        if not self.request.user.is_anonymous:
            context["is_favorite"] = Favorite.objects.filter(
                user=user, product_id=film
            ).exists()
        return context


class ProductSaveView(CreateView):
    model = Products
    form_class = FilmsForm
    template_name = "form.html"

    def form_valid(self, form):
        film = form.save(commit=False)
        message = {}
        selected_tags = self.request.POST.getlist("tags")
        if self.request.POST.get("form-name") == "sell":
            film.type = "sell"
            message["тип"] = "Продать"
            user = self.request.user
            if user.ball >= 10:
                user.ball -= 10
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
        film.tags.set(selected_tags)

        message["film_id"] = film.id
        if image:
            asyncio.run(send_message_to_channel(message, film.image.path))
        else:
            asyncio.run(send_message_to_channel(message))

        message = Message.objects.create(
            sender=self.request.user,
            message="Вы успешно отправили запрос !.",
            created_at=timezone.now(),
        )

        message.recipients.set([self.request.user])
        messages.success(self.request, "Вы успешно отправили запрос !")
        return redirect("index")

    def form_invalid(self, form):
        errors = form.errors
        for error in errors:
            messages.error(self.request, f"{errors[f'{error}'][0]}")
        # messages.error(self.request, f'{errors}')
        return render(
            self.request, self.template_name, {"form": form, "errors": errors}
        )


class FilmsUpdateView(UpdateView):
    model = Products
    form_class = FilmsForm
    template_name = "form.html"  # Update with your template path
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
        type_product = self.request.POST.get("type")
        category = self.request.POST.get("category")
        sub_category = self.request.POST.get("sub_category")
        tags = self.request.POST.get("tags")
        city = self.request.POST.get("city")
        country = self.request.POST.get("country")

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

        if search_form.is_valid():
            query = search_form.cleaned_data.get("query")
            latin_query = to_latin(query).lower()
            cyrillic_query = to_cyrillic(query).lower()
            filter1 = (
                queryset.filter(
                    Q(title__startswith=latin_query)
                    | Q(description__startswith=latin_query)
                    | Q(title__contains=latin_query)
                    | Q(description__contains=latin_query)
                    | Q(title__startswith=cyrillic_query)
                    | Q(description__startswith=cyrillic_query)
                    | Q(title__contains=cyrillic_query)
                    | Q(description__contains=cyrillic_query)
                )
                .annotate(
                    title_order=Case(
                        When(title__startswith=latin_query, then=Value(1)),
                        When(title__contains=latin_query, then=Value(2)),
                        When(title__startswith=cyrillic_query, then=Value(3)),
                        When(title__contains=cyrillic_query, then=Value(4)),
                        default=Value(5),
                        output_field=CharField(),
                    ),
                    description_order=Case(
                        When(description__startswith=latin_query, then=Value(1)),
                        When(description__contains=latin_query, then=Value(2)),
                        When(description__startswith=cyrillic_query, then=Value(3)),
                        When(description__contains=cyrillic_query, then=Value(4)),
                        default=Value(5),
                        output_field=CharField(),
                    ),
                )
                .order_by("title_order", "description_order")
            )

            if filter1:
                context["films"] = filter1
            else:
                thresholds = [90, 70, 50, 30]
                filter2 = None
                for threshold in thresholds:
                    filter2 = self.fuzzywuzzy_search(
                        latin_query, cyrillic_query, queryset, threshold
                    )
                    if filter2:
                        break
                context["films"] = filter2
        else:
            companies = User.objects.filter(is_business_account=True)
            if type_product != "company":
                filter3 = None
                if type_product != "all":
                    filter3 = queryset.filter(type=type_product)
                else:
                    ...
                if category:
                    filter3 = queryset.filter(category=category)
                    if sub_category:
                        filter3 = queryset.filter(sub_category=sub_category)
                if country:
                    filter3 = queryset.filter(country=country)
                    if city:
                        filter3 = queryset.filter(city=city)
                context["films"] = filter3
            else:
                if category:
                    companies = companies.filter(category=category)
                    if sub_category:
                        companies = companies.filter(sub_category=sub_category)
                context["companies"] = companies
        return render(request, self.template_name, context=context)

    # def get_queryset(self):
    #     queryset = Products.objects.filter(is_active=True, is_published=True).order_by(
    #         "-create_date"
    #     )
    #     form = SearchForm(self.request.GET)
    #     category = self.request.GET.get("category")
    #     sub_category = self.request.GET.get("sub_category")
    #     tags = self.request.GET.getlist("tags")
    #     country = self.request.GET.get("country")
    #     city = self.request.GET.get("city")
    #     type_product = self.request.GET.get("type")
    #     if type_product != "company":
    #         if form.is_valid():
    #             query = form.cleaned_data["query"]
    #             latin_query = to_latin(query)
    #             cyrillic_query = to_cyrillic(query)
    #             q_kirill = Q(title__icontains=cyrillic_query) | Q(
    #                 description__icontains=cyrillic_query
    #             )
    #             q_latin = Q(title__icontains=latin_query) | Q(
    #                 description__icontains=latin_query
    #             )
    #
    #             products = Products.objects.filter(q_kirill | q_latin).filter(
    #                 is_active=True, is_published=True
    #             )
    #
    #             if products:
    #                 queryset = products
    #             else:
    #                 similar_products = self.fuzzywuzzy_search(
    #                     latin_query, cyrillic_query, queryset, 80
    #                 )
    #                 if similar_products:
    #                     queryset = similar_products
    #                 else:
    #                     similar_products = self.fuzzywuzzy_search(
    #                         latin_query, cyrillic_query, queryset, 50
    #                     )
    #                     if similar_products:
    #                         queryset = similar_products
    #                     else:
    #                         similar_products = self.fuzzywuzzy_search(
    #                             latin_query, cyrillic_query, queryset, 20
    #                         )
    #                         if similar_products:
    #                             queryset = similar_products
    #                         else:
    #                             print("bom bo'sh")
    #         filter_params = {}
    #
    #         if category:
    #             filter_params["category"] = category
    #         if sub_category:
    #             filter_params["sub_category"] = sub_category
    #         if country:
    #             filter_params["country"] = country
    #         if city:
    #             filter_params["city"] = city
    #         if type_product and type_product != "all":
    #             filter_params["type"] = type_product
    #         if tags:
    #             tag_filters = Q()
    #             for tag_id in tags:
    #                 tag_filters |= Q(tags__id=tag_id)
    #             queryset = queryset.filter(
    #                 tag_filters, is_active=True, is_published=True
    #             )
    #
    #         if filter_params:
    #             queryset = queryset.filter(
    #                 **filter_params, is_published=True, is_active=True
    #             )
    #         return queryset
    #     else:
    #         companies = User.objects.none()
    #         if category:
    #             companies = User.objects.filter(
    #                 is_business_account=True,
    #                 category=category,
    #             )
    #             if sub_category:
    #                 companies = User.objects.filter(
    #                     is_business_account=True,
    #                     category=category,
    #                     sub_category=sub_category,
    #                 )
    #         else:
    #             companies = User.objects.filter(is_business_account=True)
    #         return companies

    # def post(self, request, **kwargs):
    #     # context = self.get_context_data(object_list=Products.objects.none(), **kwargs)
    #     context = {
    #         "films": Products.objects.filter(
    #             is_active=True, is_published=True
    #         ).order_by("-create_date"),
    #     }
    #     form = SearchForm(request.POST)
    #     queryset = Products.objects.all()
    #     category = request.POST.get("category")
    #     sub_category = request.POST.get("sub_category")
    #     tags = request.POST.getlist("tags")
    #     country = request.POST.get("country")
    #     city = request.POST.get("city")
    #     type_product = request.POST.get("type")
    #
    #     if form.is_valid():
    #         if type_product == "company":
    #             companies = User.objects.filter(is_business_account=True)
    #             # context["companies"] = companies
    #             return render(self.request, self.template_name, context)
    #             # return redirect("product-list")
    #         else:
    #             query = form.cleaned_data["query"]
    #             latin_query = to_latin(query)
    #             cyrillic_query = to_cyrillic(query)
    #
    #             q_kirill = Q(title__icontains=cyrillic_query) | Q(
    #                 description__icontains=cyrillic_query
    #             )
    #             q_latin = Q(title__icontains=latin_query) | Q(
    #                 description__icontains=latin_query
    #             )
    #
    #             products = Products.objects.filter(
    #                 q_kirill | q_latin, is_active=True, is_published=True
    #             )
    #
    #             if not products.exists():
    #                 similar_products = self.fuzzywuzzy_search(
    #                     latin_query, cyrillic_query, queryset, 80
    #                 )
    #                 if not similar_products:
    #                     similar_products = self.fuzzywuzzy_search(
    #                         latin_query, cyrillic_query, queryset, 50
    #                     )
    #                     if not similar_products:
    #                         similar_products = self.fuzzywuzzy_search(
    #                             latin_query, cyrillic_query, queryset, 20
    #                         )
    #                         if similar_products:
    #                             queryset = similar_products
    #                         else:
    #                             print("bom bo'sh")
    #
    #             filter_params = {}
    #
    #             if category:
    #                 filter_params["category"] = category
    #             if sub_category:
    #                 filter_params["sub_category"] = sub_category
    #             if country:
    #                 filter_params["country"] = country
    #             if city:
    #                 filter_params["city"] = city
    #             if type_product and type_product != "all":
    #                 filter_params["type"] = type_product
    #             if tags:
    #                 tag_filters = Q()
    #                 for tag_id in tags:
    #                     tag_filters |= Q(tags__id=tag_id)
    #                 queryset = queryset.filter(
    #                     tag_filters, is_active=True, is_published=True
    #                 )
    #
    #             if filter_params:
    #                 queryset = queryset.filter(
    #                     **filter_params, is_published=True, is_active=True
    #                 )
    #
    #         context["films"] = queryset
    #         return render(self.request, self.template_name, context)


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
