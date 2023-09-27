import asyncio

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView

from .forms import FilmsForm, ProductFilterForm
from .models import Films, SubCategories, Favorite, Tag
from .utils import send_message_to_channel


class IndexView(ListView):
    template_name = "index.html"
    context_object_name = "films_buy"

    def get_queryset(self):
        return Films.objects.filter(type='Купить', is_active=True, is_published=True).order_by('-create_date')[:7]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["films_sell"] = Films.objects.filter(type='sell', is_active=True, is_published=True).order_by(
            '-create_date')[:7]
        context["films_buy"] = Films.objects.filter(type='buy', is_active=True, is_published=True).order_by(
            '-create_date')[:7]
        context["title"] = "Запросы: "
        context["form"] = FilmsForm()

        user = self.request.user
        if user.is_authenticated:
            favorite_products = Favorite.objects.filter(user=user).values_list('product_id', flat=True)
            context['favorite_products'] = list(favorite_products)

        return context

    @staticmethod
    def post(request):
        form = FilmsForm(request.POST)
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

            film.save()
            message['film_id'] = film.id
            asyncio.run(send_message_to_channel(message))
            messages.success(request, 'Отправлено на модерацию')
            return redirect('index')
        else:
            messages.error(request, list(form.errors.values())[0][0])
            return redirect('index')


class ProductDetailView(DetailView):
    model = Films
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
        return Films.objects.filter(pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        film = self.object

        if not self.request.user.is_anonymous:
            context["is_favorite"] = Favorite.objects.filter(user=user,
                                                             product_id=film).exists()
        return context


class ProductSaveView(CreateView):
    model = Films
    form_class = FilmsForm
    template_name = 'form.html'

    def form_valid(self, form):
        film = form.save(commit=False)
        message = {}
        selected_tags = self.request.POST.getlist('tags')
        if self.request.POST.get('form-name') == "sell":
            film.type = 'sell'
            message['тип'] = 'Продать'
        else:
            message['тип'] = 'Купить'

        film.author = self.request.user

        image = self.request.FILES.get('image')

        if image:
            film.image = image

        film.is_published = True

        for field_name, field_value in form.cleaned_data.items():
            message[field_name] = field_value

        film.save()
        film.tags.set(selected_tags)

        message['film_id'] = film.id
        asyncio.run(send_message_to_channel(message, film.image.path))

        messages.success(self.request, "Вы успешно отправили запрос !")
        return super().form_valid(form)

    def form_invalid(self, form):
        error_message = list(form.errors.values())[0][0]
        messages.error(self.request, error_message)
        # messages.error(self.request, form.errors)
        return redirect("add_film")


class FilmsListView(ListView):
    model = Films
    template_name = 'product-list.html'
    context_object_name = 'films'
    paginate_by = 24

    def get_queryset(self):
        queryset = Films.objects.filter(is_active=True, is_published=True)
        category = self.request.GET.get('category')
        sub_category = self.request.GET.get('sub_category')
        tags = self.request.GET.getlist('tags')
        country = self.request.GET.get('country')
        city = self.request.GET.get('city')
        type_product = self.request.GET.get('type')

        filter_params = {}

        if category:
            filter_params['category'] = category
        if sub_category:
            filter_params['sub_category'] = sub_category
        if country:
            filter_params['country'] = country
        if city:
            filter_params['city'] = city
        if city:
            filter_params['type'] = type_product

        if tags:
            # Создаем Q-объект для фильтрации по тегам с "или" условием
            tag_filters = Q()
            for tag_id in tags:
                tag_filters |= Q(tags__id=tag_id)
            queryset = queryset.filter(tag_filters)

        if filter_params:
            queryset = queryset.filter(**filter_params)

        return queryset.order_by('-create_date')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProductFilterForm(self.request.GET)  # Используйте GET параметры для формы
        return context


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


# def up_to_recommendation(request, pk):
#     time_now = datetime.datetime.now().__str__()
#     film = Films.objects.filter(pk=pk).first()
#     film.create_date = time_now
#     user = User.objects.get(pk=request.user.id)
#     if user.score >= 5:
#         user.score = user.score - 5
#         user.save()
#     else:
#         messages.error(request, "Sizda maglag'  yetarli emas")
#         return redirect('profile', request.user.id)
#     film.save()
#     return redirect('profile', request.user.id)

@login_required
def add_to_favorite(request, pk):
    product = get_object_or_404(Films, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product_id=product)

    if created:
        product.in_favorites = True
        product.save()

    return JsonResponse({"is_favorite": True})


@login_required
def remove_from_favorite(request, pk):
    product = get_object_or_404(Films, pk=pk)
    favorite = Favorite.objects.filter(user=request.user, product_id=product).first()

    if favorite:
        favorite.delete()
        product.in_favorites = False
        product.save()

    return JsonResponse({"is_favorite": False})
