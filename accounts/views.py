import random
import string

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.shortcuts import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from films.forms import FilmsForm
from films.models import Films, Favorite
from .forms import UserLoginForm, UserRegisterForm


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=4))


class RegisterUserView(CreateView):
    form_class = UserRegisterForm
    template_name = 'user/register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['register_form'] = self.form_class
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        code = generate_verification_code()
        user.save()

        subject = 'Ibroxim'
        message = f"{code}"
        from_email = settings.EMAIL_HOST_USER
        to = [user.email]
        try:
            send_mail(subject, message, from_email, to)
        except:
            messages.error(self.request,
                           f"Проблема с отправкой электронного письма на адрес {to}. Проверьте, правильно ли вы его ввели.")
            return render(self.request, self.template_name, {'register_form': form})
        self.request.session['verification_code'] = code
        self.request.session['user_id'] = user.pk
        return redirect('verify_code')

    def form_invalid(self, form):
        errors = form.errors
        return render(self.request, self.template_name, {'register_form': form})


class VerifyCodeView(View):
    template_name = "user/verify_code.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        verification_code = request.session.get('verification_code')  # Получить код из сессии
        user_id = request.session.get('user_id')
        User = get_user_model()

        if verification_code and user_id:
            entered_code = request.POST.get('verification_code')

            try:
                user = User.objects.get(id=user_id, is_active=False)
                if entered_code == verification_code:
                    user.is_active = True
                    user.save()
                    login(request, user)
                    messages.success(request,
                                     "Ваша учетная запись была успешно активирована.")
                    # return redirect('profile', request.user.pk)
                    return redirect('index')
                else:
                    messages.error(request, "Неверный код подтверждения. Пожалуйста, попробуйте еще раз.")
            except Exception as e:
                messages.error(request, "Произошла ошибка при активации учетной записи.")
                return redirect('register')  # Можно перенаправить на страницу регистрации или на другую страницу
        else:
            messages.error(request,
                           "Код подтверждения не найден в сессии. Пожалуйста, пройдите процесс регистрации заново.")
            return redirect('register')  # Можно перенаправить на страницу регистрации или на другую страницу


class LoginUserView(LoginView):
    form_class = UserLoginForm
    template_name = 'user/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_form'] = self.form_class
        return context

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, "Вы успешно вошли в систему !")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        # Возвращаем страницу регистрации с заполненными данными пользователя
        return render(self.request, self.template_name, {'login_form': form})

    def get_success_url(self):
        return reverse("index")


class LogoutUserView(LogoutView):
    def get_next_page(self):
        messages.success(self.request, "Вы успешно вышли из аккаунта !")
        return super().get_next_page()


@method_decorator(login_required, name='dispatch')
class ProfileView(DetailView):
    model = get_user_model()
    template_name = "user/profile.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"{self.object.first_name} {self.object.last_name}"
        context["user"] = self.model.objects.get(pk=self.kwargs['pk'])
        context["products"] = Films.objects.filter(author_id=self.object.pk).order_by('-create_date')
        favorite_product_ids = Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True)
        if self.request.user.is_authenticated:
            in_favorite = list(favorite_product_ids)
        else:
            in_favorite = []
        context['in_favorite'] = in_favorite
        # Получите все продукты, которые есть в списке избранных
        context["favorite_products"] = Films.objects.filter(id__in=favorite_product_ids).order_by('-create_date')
        return context


class ProductActionView(View):
    @staticmethod
    def post(request):
        data = request.POST
        action = data.get("action")
        selected_product_ids = data.getlist("selected_products")

        if action == "delete":
            Films.objects.filter(pk__in=selected_product_ids).delete()
        elif action == "edit":
            return redirect('index')
            # return redirect('product-edit', pk=int(selected_product_ids[0]))
        elif action == "activate":
            Films.objects.filter(pk__in=selected_product_ids).update(is_published=True)
        elif action == "deactivate":
            Films.objects.filter(pk__in=selected_product_ids).update(is_published=False)
        return JsonResponse({"message": "Действие успешно выполнено"})


class EditProductsView(UpdateView):
    model = Films
    form_class = FilmsForm
    template_name = 'edit-product.html'
    context_object_name = 'form'

    def get_queryset(self):
        return get_object_or_404(Films, pk=self.kwargs['pk'])

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("profile", kwargs={
            "pk": self.kwargs["pk"]
        })
