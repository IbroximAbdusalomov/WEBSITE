import asyncio

import emoji
from cyrtranslit import to_cyrillic, to_latin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from fuzzywuzzy import fuzz

from accounts.models import Message, User
from .forms import FilmsForm, ProductFilterForm, SearchForm
from .models import Products, SubCategories, Favorite, Tag
from .utils import send_message_to_channel


class IndexView(ListView):
    template_name = "index.html"
    context_object_name = "films_buy"

    def get_queryset(self):
        return Products.objects.filter(type='buy', is_active=True, is_published=True).order_by(
            '-create_date')[:8]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["films_sell"] = Products.objects.filter(type='sell', is_active=True, is_published=True).order_by(
            '-create_date')[:8]
        context["title"] = "Запросы: "
        context["form"] = FilmsForm()
        if self.request.user.is_authenticated:
            in_favorite = list(Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True))
        else:
            in_favorite = []
        context['in_favorite'] = in_favorite
        context['jobs'] = Products.objects.filter(is_active=True, is_published=True, category__slug='texnolog')
        return context

    @staticmethod
    def post(request):
        context = {
            "films_buy": Products.objects.filter(type='buy', is_active=True, is_published=True).order_by(
                '-create_date')[:8],
            "films_sell": Products.objects.filter(type='sell', is_active=True, is_published=True).order_by(
                '-create_date')[:8],
            "title": "Запросы: ",
            # "form": FilmsForm(),
        }
        form = FilmsForm(request.POST)
        selected_tags = request.POST.getlist('tags')
        if form.is_valid():
            film = form.save(commit=False)
            if not request.user.is_anonymous:
                film.author = request.user
                film.email = request.user.email
            film.is_published = True
            film.image = 'product-images/image.png'
            message = {}

            for field_name, field_value in form.cleaned_data.items():
                message[field_name] = field_value
            message['тип'] = 'Купить'

            try:
                price = float(
                    form.cleaned_data.get('price', 0))
                film.price = price
            except ValueError:
                film.price = None
            film.save()
            film.tags.set(selected_tags)
            message['film_id'] = film.id
            asyncio.run(send_message_to_channel(message))
            messages.success(request, 'Отправлено на модерацию')
            return redirect('index')
        else:
            context['form'] = form
            context['errors'] = form.errors
            return render(request, 'index.html', context=context)


class ProductDetailView(DetailView):
    model = Products
    template_name = "product-details.html"
    context_object_name = "product"

    def dispatch(self, request, *args, **kwargs):
        film = self.get_object()
        session_key = 'film_{}_viewed'.format(film.pk)

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
            context["is_favorite"] = Favorite.objects.filter(user=user,
                                                             product_id=film).exists()
        return context


class ProductSaveView(CreateView):
    model = Products
    form_class = FilmsForm
    template_name = 'form.html'

    def form_valid(self, form):
        film = form.save(commit=False)
        message = {}
        selected_tags = self.request.POST.getlist('tags')
        if self.request.POST.get('form-name') == "sell":
            film.type = 'sell'
            message['тип'] = 'Продать'
            user = self.request.user
            if user.ball >= 10:
                user.ball -= 10
                user.save()
        else:
            film.price = None
            message['тип'] = 'Купить'

        film.author = self.request.user if not self.request.user.is_anonymous else None
        if form.cleaned_data['is_price_negotiable'] or not form.cleaned_data['price']:
            film.price = None

        image = self.request.FILES.get('image')

        if image:
            film.image = image

        film.is_published = True

        for field_name, field_value in form.cleaned_data.items():
            message[field_name] = field_value

        film.save()
        film.tags.set(selected_tags)

        message['film_id'] = film.id
        if image:
            asyncio.run(send_message_to_channel(message, film.image.path))
        else:
            asyncio.run(send_message_to_channel(message))

        message = Message.objects.create(
            sender=self.request.user,
            message="Вы успешно отправили запрос !.",
            created_at=timezone.now()
        )

        message.recipients.set([self.request.user])
        messages.success(self.request, "Вы успешно отправили запрос !")
        return redirect('index')

    def form_invalid(self, form):
        errors = form.errors
        for error in errors:
            messages.error(self.request, f"{errors[f'{error}'][0]}")
        # messages.error(self.request, f'{errors}')
        return render(self.request, self.template_name, {'form': form, 'errors': errors})


class FilmsUpdateView(UpdateView):
    model = Products
    form_class = FilmsForm
    template_name = 'form.html'  # Update with your template path
    success_url = '/success/'  # Redirect to a success page after updating
    context_object_name = 'film'  # Optional: Customize the context object name

    def get_object(self, queryset=None):
        return Products.objects.get(pk=self.kwargs['pk'])


class FilmsListView(ListView):
    model = Products
    template_name = 'product-list.html'
    # paginate_by = 24
    context_object_name = 'films'

    def get_queryset(self):
        queryset = Products.objects.filter(is_active=True, is_published=True).order_by('-create_date')
        form = SearchForm(self.request.GET)
        category = self.request.GET.get('category')
        sub_category = self.request.GET.get('sub_category')
        tags = self.request.GET.getlist('tags')
        country = self.request.GET.get('country')
        city = self.request.GET.get('city')
        type_product = self.request.GET.get('type')

        if form.is_valid():
            query = form.cleaned_data['query']
            latin_query = to_latin(query)
            cyrillic_query = to_cyrillic(query)
            q_kirill = Q(title__icontains=cyrillic_query) | Q(description__icontains=cyrillic_query)
            q_latin = Q(title__icontains=latin_query) | Q(description__icontains=latin_query)

            products = Products.objects.filter(
                q_kirill | q_latin
            ).filter(is_active=True, is_published=True)

            if products:
                queryset = products
            else:
                similar_products = self.fuzzywuzzy_search(latin_query, cyrillic_query, queryset, 80)
                if similar_products:
                    queryset = similar_products
                else:
                    similar_products = self.fuzzywuzzy_search(latin_query, cyrillic_query, queryset, 50)
                    if similar_products:
                        queryset = similar_products
                    else:

                        similar_products = self.fuzzywuzzy_search(latin_query, cyrillic_query, queryset, 20)
                        if similar_products:
                            queryset = similar_products
                        else:
                            print("bom bo'sh")
        filter_params = {}

        if category:
            filter_params['category'] = category
        if sub_category:
            filter_params['sub_category'] = sub_category
        if country:
            filter_params['country'] = country
        if city:
            filter_params['city'] = city
        if type_product and type_product != 'all':
            filter_params['type'] = type_product
        if tags:
            tag_filters = Q()
            for tag_id in tags:
                tag_filters |= Q(tags__id=tag_id)
            queryset = queryset.filter(tag_filters, is_active=True, is_published=True)

        if filter_params:
            queryset = queryset.filter(**filter_params, is_published=True, is_active=True)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProductFilterForm(self.request.GET)  # Используйте GET параметры для формы
        if self.request.user.is_authenticated:
            in_favorite = list(Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True))
        else:
            in_favorite = []
        context['in_favorite'] = in_favorite
        # context['films'] = Films.objects.filter(is_active=True, is_published=True).order_by('-create_date')
        context['top_films'] = Products.objects.filter(is_active=True, is_published=True, is_top_film=True).order_by(
            '-create_date')
        context['companies'] = User.objects.filter(is_business_account=True)
        context['search'] = SearchForm()

        return context

    def fuzzywuzzy_search(self, latin_query, cyrillic_query, queryset, threshold):
        similar_products = []

        # Создаем множества слов из латинской и кириллической строки запроса
        latin_words = set(latin_query.split())
        cyrillic_words = set(cyrillic_query.split())

        for product in queryset:
            # Создаем множества слов из названия и описания продукта
            product_title_words = set(product.title.split())
            product_description_words = set(product.description.split())

            # Проверяем сходство слов с латинскими словами в названии
            latin_similarity_title = any(fuzz.token_set_ratio(word1, word2) >= threshold
                                         for word1 in product_title_words
                                         for word2 in latin_words)

            # Проверяем сходство слов с кириллическими словами в названии
            cyrillic_similarity_title = any(fuzz.token_set_ratio(word1, word2) >= threshold
                                            for word1 in product_title_words
                                            for word2 in cyrillic_words)

            # Проверяем сходство слов с латинскими словами в описании
            latin_similarity_description = any(fuzz.token_set_ratio(word1, word2) >= threshold
                                               for word1 in product_description_words
                                               for word2 in latin_words)

            # Проверяем сходство слов с кириллическими словами в описании
            cyrillic_similarity_description = any(fuzz.token_set_ratio(word1, word2) >= threshold
                                                  for word1 in product_description_words
                                                  for word2 in cyrillic_words)

            # Если есть сходство хотя бы с одним словом из запроса, добавляем продукт в список
            if (latin_similarity_title or cyrillic_similarity_title or
                    latin_similarity_description or cyrillic_similarity_description):
                similar_products.append(product)

        return similar_products


def related_to_it(request):
    category_id = request.GET.get('category_id', None)
    subcategory_id = request.GET.get('subcategory_id', None)

    sub_categories = {}
    if category_id:
        subcategories = SubCategories.objects.filter(category_id=category_id).all()
        sub_categories = {subcategory.id: subcategory.name for subcategory in subcategories}

    tags = {}
    if subcategory_id:
        tags_query = Tag.objects.filter(subcategory=subcategory_id)
        tags = {tag.id: tag.name for tag in tags_query}

    return JsonResponse({'subcategories': sub_categories, 'tags': tags})


@login_required()
def add_to_favorites(request, pk):
    product = Products.objects.get(pk=pk)
    try:
        favorite = Favorite.objects.get(user=request.user, product_id=product)
        favorite.delete()
        response_data = {'added': False}
    except Favorite.DoesNotExist:
        Favorite.objects.create(user=request.user, product_id=product)
        response_data = {'added': True}
    return JsonResponse(response_data)


# else:
#     return redirect('login')


# @login_required
def favorite_list(request):
    favorites = {"favorites": Favorite.objects.filter(user=request.user)}
    return JsonResponse(favorites)


def send_message(request, text=None):
    if request.method == 'POST' and text:
        messages.error(request, text)
        return JsonResponse({'message': 'Message sent successfully'})
    return JsonResponse({'message': 'Invalid request'})


def remove_emoji(text):
    return emoji.replace_emoji(text)


def get_suggestions(request):
    user_query = request.GET.get('term', '')
    latin_query = to_latin(user_query).lower()
    cyrillic_query = to_cyrillic(user_query).lower()

    all_words = set()

    for product in Products.objects.values('title', 'description'):
        title_words = product['title'].split()
        description_words = product['description'].split()
        all_words.update(title_words)
        all_words.update(description_words)

    all_words = [remove_emoji(word).lower() for word in all_words]

    filtered_words = [word for word in all_words if word.startswith(latin_query) or word.startswith(cyrillic_query)]

    suggestions = filtered_words[:5]

    def find_suggestions(query, limit):
        return [word for word in all_words if fuzz.token_set_ratio(word, query) >= limit]

    if len(suggestions) < 5:
        supplement = 5 - len(suggestions)
        filtered_words = [word for word in all_words if latin_query in word or cyrillic_query in word]
        suggestions = filtered_words[:supplement]

    for threshold in [90, 80, 70]:
        if len(suggestions) < 5:
            cyrillic_similar_words = find_suggestions(cyrillic_query, threshold)
            latin_similar_words = find_suggestions(latin_query, threshold)

            similar_words = list(set(cyrillic_similar_words + latin_similar_words))

            if similar_words:
                suggestions = similar_words[:5 - len(suggestions)]
                break

    return JsonResponse(suggestions, safe=False)
