import random
import string

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render
from django.shortcuts import reverse
from django.views import View
from django.views.generic import UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from films.models import Films, Categories
from .forms import UserLoginForm, ProfileForm
from .forms import UserRegisterForm


class AuthorizationView(View):
    """Показать формы: Авторизации и Регистрации"""

    @staticmethod
    def get(request):
        return render(request, "accounts/user_auth.html", {
            "register_form": UserRegisterForm(),
            "login_form": UserLoginForm(),
            "title": "Авторизация"
        })


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=4))


class RegisterUserView(CreateView):
    form_class = UserRegisterForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        code = generate_verification_code()
        user.save()

        subject = 'HelloDjango'
        message = f"{code}"
        from_email = settings.EMAIL_HOST_USER
        to = [user.email]
        try:
            send_mail(subject, message, from_email, to)
        except:
            messages.error(self.request, f"Problem sending email to {to}, check if you typed it correctly.")
            return redirect('index')
        self.request.session['verification_code'] = code
        self.request.session['user_id'] = user.pk
        return redirect('verify_code')

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

    def render_to_response(self, context, **response_kwargs):
        return redirect("auth")

    def get_success_url(self):
        return reverse("index")


class VerifyCodeView(View):
    template_name = 'verify_code.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        verification_code = request.session.get('verification_code')  # Получить код из сессии
        user_id = request.session.get('user_id')
        User = get_user_model()

        if verification_code and user_id:
            # Получить код верификации, отправленный пользователем, из POST-запроса
            entered_code = request.POST.get('verification_code')
            # Проверка и обработка кода верификации здесь
            try:
                user = User.objects.get(id=user_id, is_active=False)
                if entered_code == verification_code:
                    # Коды совпадают, активируем учетную запись пользователя
                    user.is_active = True
                    user.save()
                    login(request, user)
                    messages.success(request, "Your account has been activated. You can now log in.")
                    return redirect('index')
                else:
                    messages.error(request, "Invalid verification code. Please try again.")
            except User.DoesNotExist:
                messages.error(request, "Invalid verification code. Please try again.")
        else:
            messages.error(request,
                           "Verification code not found in session. Please go through the registration process again.")

        return render(request, self.template_name)


class LoginUserView(LoginView):
    form_class = UserLoginForm

    def form_valid(self, form):
        user = form.get_user()
        # if test.is_active == True:
        login(self.request, user)
        messages.success(self.request, "Вы успешно вошли в систему !")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

    def render_to_response(self, context, **response_kwargs):
        return redirect("auth")

    def get_success_url(self):
        return reverse("index")


class LogoutUserView(LogoutView):
    def get_next_page(self):
        messages.success(self.request, "Вы успешно вышли из аккаунта !")
        return super().get_next_page()


class ProfileView(DetailView):
    model = get_user_model()
    template_name = "accounts/profile.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Categories.objects.all()
        context["title"] = f"{self.object.first_name} {self.object.last_name}"
        context["user"] = self.model.objects.get(pk=self.kwargs['pk'])
        context["user_films"] = Films.objects.filter(author_id=self.object.pk).order_by('-create_date')
        return context


class EditProfileView(UpdateView):
    model = get_user_model()
    template_name = "accounts/edit_profile.html"
    form_class = ProfileForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.pk != kwargs["pk"]:
            messages.error(request, "У вас недостаточно прав для редактирования этого профиля !")
            return redirect("index")
        return super().dispatch(request, args, kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Изменения были успешно сохранены !")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("profile", kwargs={
            "pk": self.kwargs["pk"]
        })


def delete_confirm(request, pk):
    product = get_object_or_404(Films, pk=pk)
    return render(request, 'accounts/delete.html', {'product': product})


#
def delete_film(request, pk):
    product = get_object_or_404(Films, pk=pk)
    product.delete()
    return redirect('index')

# def update_confirm(request, pk):
#     product = get_object_or_404(Films, pk=pk)
#     return render(request, 'accounts/update_confirm.html', {"product": product})
#
#
# def update_film(request, pk):
#     film = Films.objects.filter(id=pk).first()
#     form = FilmsForm(request.POST, request.FILES, instance=film)
#     context = {
#         "form": form,
#     }
#     if form.is_valid():
#         objMod = form.save(commit=False)
#         objMod.save()
#         instance = Films.objects.get(id=pk)
#         instance.delete()
#         return redirect("index")
#     return render(request, "films/edit_film.html", context)
