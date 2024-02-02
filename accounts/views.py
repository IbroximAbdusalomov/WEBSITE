import asyncio
import random
import secrets
import string
import requests

from django.views import View
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.shortcuts import reverse
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db.models import Avg, Sum
from django.core.mail import send_mail
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth import login, get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import user_passes_test
from django.views.generic.edit import CreateView, UpdateView

from support.models import SupportTicket
from films.forms import FilmsForm
from films.models import Products, Favorite
from .forms import (
    UserLoginForm,
    UserRegisterForm,
    CompanyInfoForm,
    ContactInfoForm,
    DescriptionCountryForm,
    NotificationForm,
    LogoForm,
    BannerForm,
    UserProfileUpdateForm,
    ComplaintForm,
    AddBallForm,
    TopUpYourAccountForm,
)
from .models import UserRating, Message, UserSubscription, Complaint, PointsTransaction

from .utils import send_message_to_channel, true_account_status, send_message


def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(characters) for _ in range(length))
    return password


def generate_verification_code():
    return "".join(random.choices(string.digits, k=4))


def send_sms_verification_code(phone_number, code):
    # Замените следующие значения на ваши данные и ключи Infobip
    api_key = "1871b27648f478206aceb224f14851a0-03afcb56-5e8e-48f9-804b-7121e6697dd5"
    sender_id = "Ibroxim 🧑🏻‍💻"

    url = "https://api.infobip.com/sms/1/text/single"

    headers = {
        "Authorization": f"App {api_key}",
    }

    data = {
        "from": sender_id,
        "to": phone_number,
        "text": f"Your verification code is: {code}",
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("SMS sent successfully")
    else:
        print("Failed to send SMS")
        print(response.text)


class RegisterUserView(CreateView):
    form_class = UserRegisterForm
    template_name = "user/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["register_form"] = self.form_class
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        code = generate_verification_code()
        user.save()

        subject = "Ibroxim"
        message = f"{code}"
        from_email = settings.EMAIL_HOST_USER
        to = [user.email]
        try:
            send_sms_verification_code(form.cleaned_data["telephone"], message)
            send_mail(subject, message, from_email, to)
        except:
            messages.error(
                self.request,
                f"Проблема с отправкой электронного письма на адрес {to}. Проверьте, правильно ли вы его ввели.",
            )
            return render(self.request, self.template_name, {"register_form": form})
        self.request.session["verification_code"] = code
        self.request.session["user_id"] = user.pk
        return redirect("verify_code")

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return render(self.request, self.template_name, {"register_form": form})


class VerifyCodeView(View):
    template_name = "user/verify_code.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        verification_code = request.session.get(
            "verification_code"
        )  # Получить код из сессии
        user_id = request.session.get("user_id")
        # User = get_user_model()

        if verification_code and user_id:
            entered_code = request.POST.get("verification_code")

            try:
                user = get_user_model().objects.get(id=user_id, is_active=False)
                if entered_code == verification_code:
                    user.is_active = True
                    user.save()
                    login(request, user)
                    message = Message.objects.create(
                        sender=user,
                        message="Ваша учетная запись была успешно активирована.",
                        created_at=timezone.now(),
                    )

                    message.recipients.set([user])
                    messages.success(
                        request, "Ваша учетная запись была успешно активирована."
                    )

                    return redirect("index")
                else:
                    messages.error(
                        request,
                        "Неверный код подтверждения. Пожалуйста, попробуйте еще раз.",
                    )
                    return redirect(
                        "register"
                    )  # Можно перенаправить на страницу регистрации или на другую страницу
            except Exception as e:
                messages.error(
                    request, "Произошла ошибка при активации учетной записи."
                )
                return redirect(
                    "register"
                )  # Можно перенаправить на страницу регистрации или на другую страницу
        else:
            messages.error(
                request,
                "Код подтверждения не найден в сессии. Пожалуйста, пройдите процесс регистрации заново.",
            )
            return redirect(
                "register"
            )  # Можно перенаправить на страницу регистрации или на другую страницу


class LoginUserView(LoginView):
    form_class = UserLoginForm
    template_name = "user/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_form"] = self.form_class
        return context

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, "Вы успешно вошли в систему !")
        message = Message.objects.create(
            sender=user,
            message="Ваша учетная запись была успешно активирована.",
            created_at=timezone.now(),
        )

        message.recipients.set([self.request.user])
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Имя пользователя или пароль неверные. Пожалуйста, попробуйте снова.",
        )
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("index")


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    template_name = "user/update.html"
    form_class = UserProfileUpdateForm

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Ваш профиль был успешно обновлен.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Пожалуйста, исправьте ошибки в форме.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("myaccount")


class LogoutUserView(LogoutView):
    def get_next_page(self):
        user = self.request.user
        messages.success(self.request, "Вы успешно вышли из аккаунта !")
        message = Message.objects.create(
            sender=user,
            message="Ваша учетная запись была успешно активирована.",
            created_at=timezone.now(),
        )

        message.recipients.set([user])
        return super().get_next_page()


class MyAccountRedirectView(DetailView):
    model = get_user_model()
    # model = User
    template_name = "user/profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"{self.object.first_name} {self.object.last_name}"
        context["user"] = self.model.objects.get(pk=self.request.user.pk)
        context["products"] = Products.objects.filter(
            author_id=self.object.pk
        ).order_by("-create_date")
        favorite_product_ids = Favorite.objects.filter(
            user=self.request.user
        ).values_list("product_id", flat=True)
        if self.request.user.is_authenticated:
            in_favorite = list(favorite_product_ids)
        else:
            in_favorite = []
        context["in_favorite"] = in_favorite
        context["favorite_products"] = Products.objects.filter(
            id__in=favorite_product_ids
        ).order_by("-create_date")
        notifications = Message.objects.filter(
            recipients=self.request.user, is_read=False
        ).exists()
        if notifications:
            context["notification"] = False
        else:
            context["notification"] = True
        seen = Products.objects.filter(author_id=self.request.user.pk).aggregate(
            Sum("view_count")
        )["view_count__sum"]
        view_telephone_product = Products.objects.filter(
            author_id=self.request.user.pk
        ).aggregate(Sum("telephone_view_count"))["telephone_view_count__sum"]
        context["count_all_views_product"] = seen if seen else 0
        context["count_all_favorite_product"] = Favorite.objects.filter(
            product_id__author_id=self.request.user.pk
        ).count()
        context["count_all_view_telephone_product"] = (
            view_telephone_product if view_telephone_product else 0
        )

        return context

    def post(self, request, *args, **kwargs):
        data = request.POST
        action = str(data.get("action"))
        selected_product_ids = data.getlist("selected_products")
        film = Products.objects.get(pk=int(selected_product_ids[0]))
        user = request.user

        if action == "delete":
            Products.objects.filter(pk__in=selected_product_ids).delete()
            messages.success(request, "{} был удален".format(film.pk))
            message = Message.objects.create(
                sender=user,
                message="{}: был удален.".format(film.pk),
                created_at=timezone.now(),
            )

            message.recipients.set([user])

        elif action == "edit":
            return redirect("product-edit", int(selected_product_ids[0]))
            # form = FilmsForm(instance=film)
            # return render(request, 'user/edit-product.html', {'form': form})

        elif action == "activate":
            Products.objects.filter(pk__in=selected_product_ids).update(
                is_published=True
            )
            messages.success(request, "{} был активирован".format(film.pk))
            message = Message.objects.create(
                sender=user,
                message="{}: был активирован.".format(film.pk),
                created_at=timezone.now(),
            )

            message.recipients.set([user])

        elif action == "deactivate":
            Products.objects.filter(pk__in=selected_product_ids).update(
                is_published=False
            )
            messages.success(request, "{} был деактивирован".format(film.pk))
            message = Message.objects.create(
                sender=user,
                message="{}: был деактивирован.".format(film.pk),
                created_at=timezone.now(),
            )

            message.recipients.set([user])

        elif action.startswith("up_to_recommendation"):
            if not film.is_top_film:
                if user.ball >= 10:
                    if action.endswith("1"):
                        film.top_duration = 1
                    elif action.endswith("2"):
                        film.top_duration = 3
                    elif action.endswith("3"):
                        film.top_duration = 7
                    user.ball -= 10
                    film.save()
                    user.save()
                    message = Message.objects.create(
                        sender=user,
                        message="{}: был поднят в топ.".format(film.title),
                        created_at=timezone.now(),
                    )

                    messages.success(request, "{} был поднять в топ".format(film.pk))

                    message.recipients.set([user])
                else:
                    message = Message.objects.create(
                        sender=user,
                        message="У вас не достаточно баллов поднятия в топ. \n Баллы: {}".format(
                            user.ball
                        ),
                        created_at=timezone.now(),
                    )
                    messages.success(
                        request,
                        "У вас не достаточно баллов поднятия в топ. \n Баллы: {}".format(
                            user.ball
                        ),
                    )

                    message.recipients.set([user])
            else:
                message = Message.objects.create(
                    sender=user,
                    message="Этот продуктуже был пожнять в топ пожалуйста ждите окончание срока",
                    created_at=timezone.now(),
                )

                messages.success(
                    request,
                    "Этот продуктуже был пожнять в топ пожалуйста ждите окончание срока".format(
                        film.pk
                    ),
                )

                message.recipients.set([user])
        elif action == "up_to_top":
            user = request.user
            if user.ball >= 10:
                user.ball -= 10
                film.create_date = timezone.now()
                film.create_date_changed = True
                film.save()
                user.save()
                message = Message.objects.create(
                    sender=user,
                    message="Этот продуктуже был подять в топ !!!",
                    created_at=timezone.now(),
                )

                messages.success(
                    request, "Этот продуктуже был подять в топ !!!".format(film.pk)
                )

                message.recipients.set([user])
        return redirect("myaccount")


class ProductActionView(View):
    def post(self, request):
        data = request.POST
        action = str(data.get("action"))
        selected_product_ids = data.getlist("selected_products")

        if action == "delete":
            Products.objects.filter(pk__in=selected_product_ids).delete()
        elif action == "edit":
            ...
        elif action == "activate":
            Products.objects.filter(pk__in=selected_product_ids).update(
                is_published=True
            )
        elif action == "deactivate":
            Products.objects.filter(pk__in=selected_product_ids).update(
                is_published=False
            )
        elif action.startswith("up_to_recommendation"):
            user = request.user
            if user.ball >= 10:
                user.ball -= 10
                film = Products.objects.get(pk=int(selected_product_ids[0]))
                # film.create_date = timezone.now()
                if action.endswith("1"):
                    film.top_duration = 1
                elif action.endswith("2"):
                    film.top_duration = 3
                elif action.endswith("3"):
                    film.top_duration = 7
                film.save()
                user.save()
                message = Message.objects.create(
                    sender=user,
                    message="{}: был поднят в топ.".format(film.title),
                    created_at=timezone.now(),
                )

                message.recipients.set([user])
            else:
                message = Message.objects.create(
                    sender=user,
                    message="У вас не достаточно баллов поднятия в топ. \n Баллы: {}".format(
                        user.ball
                    ),
                    created_at=timezone.now(),
                )

                message.recipients.set([user])


class EditProductsView(UpdateView):
    model = Products
    form_class = FilmsForm
    template_name = "user/edit-product.html"
    context_object_name = "form"

    def get_object(self, queryset=None):
        return get_object_or_404(Products, pk=self.kwargs["pk"])

    def form_valid(self, form):
        messages.success(self.request, "Вы успешно обновили пост!!!")
        message = Message.objects.create(
            sender=self.request.user,
            message="Вы успешно обновили пост!!!",
            created_at=timezone.now(),
        )

        message.recipients.set([self.request.user])
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("myaccount")


class CreateBusinessAccountView(View):
    template_name = "user/create_company.html"
    form_classes = [
        CompanyInfoForm,
        ContactInfoForm,
        LogoForm,
        BannerForm,
        DescriptionCountryForm,
    ]
    success_url = "myaccount"

    def get(self, request, *args, **kwargs):
        self.form_list = [form_class() for form_class in self.form_classes]
        return render(request, self.template_name, {"forms": self.form_list, "step": 0})

    def post(self, request, *args, **kwargs):
        step = int(request.POST.get("step", 0))
        self.form_list = [
            form_class(request.POST, request.FILES) for form_class in self.form_classes
        ]

        if step <= len(self.form_classes) - 1:
            current_form = self.form_list[step]
            if current_form.is_valid():
                current_data = current_form.cleaned_data
                company = get_user_model().objects.get(pk=self.request.user.pk)

                for key, value in current_data.items():
                    if key == "tags":
                        tags = value
                        company.tags.set(tags)
                    else:
                        setattr(company, key, value)
                company.is_business_account = False
                company.save()

                if step < len(self.form_classes) - 1:
                    return render(
                        request,
                        self.template_name,
                        {"forms": self.form_list, "step": step + 1},
                    )  # Увеличьте step на 1
                else:
                    # true_account_status(self.request.user.pk)
                    message = {
                        "company_name": company.company_name,
                        "telephone": company.telephone,
                        "email": company.email,
                        "category": company.category,
                        "sub_category": company.sub_category,
                        "tags": company.tags,
                        "telegram": company.telegram,
                        "whatsapp": company.whatsapp,
                        "website": company.website,
                        "url_maps": company.url_maps,
                        "description": company.description,
                        "country": company.country,
                    }

                    asyncio.run(
                        send_message_to_channel(message, pk=self.request.user.pk)
                    )
                    message = Message.objects.create(
                        sender=self.request.user,
                        message="Вы успешно создали бизнес аккаунт.",
                        created_at=timezone.now(),
                    )

                    message.recipients.set([self.request.user])
                    messages.success(self.request, "Вы успешно создали бизнес аккаунт.")
                    return redirect("myaccount")
            else:
                for field, errors in current_form.errors.items():
                    for error in errors:
                        messages.error(
                            request,
                            f"Ошибка в поле '{current_form[field].label}': {error}",
                        )
                return render(
                    request,
                    self.template_name,
                    {
                        "forms": self.form_list,
                        "step": step,
                        "errors": current_form.errors,
                    },
                )  # Удалите -1 из step
        else:
            return render(
                request, self.template_name, {"forms": self.form_list, "step": step}
            )


class ProfileView(DetailView):
    model = get_user_model()
    template_name = "user/company-profile.html"
    context_object_name = "profile"
    pk_url_kwarg = "pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = context["profile"]
        context["products"] = Products.objects.filter(
            author=user, is_published=True, is_active=True
        )
        context["average_rating"] = user.calculate_average_rating()
        context["has_rated"] = (
            UserRating.objects.filter(rater=self.request.user, rated_user=user).exists()
            if not self.request.user.is_anonymous
            else None
        )
        context["companies"] = self.model.objects.filter(
            is_business_account=True
        ).order_by("-date_joined")[:3]
        context["profile_subscription"] = None
        if self.request.user.is_authenticated:
            context["profile_subscription"] = UserSubscription.objects.filter(
                subscriber=self.request.user, target_user=self.object
            ).first()
        context["followers"] = UserSubscription.objects.filter(
            target_user=self.object
        ).count()
        context["verified"] = True
        context["form"] = ComplaintForm()

        return context


@login_required
def add_rating(request, evaluator_id, user_id, grade):
    try:
        evaluator_id = int(evaluator_id)
        user_id = int(user_id)
        grade = int(grade)

        rating, created = UserRating.objects.get_or_create(
            rater_id=evaluator_id, rated_user_id=user_id, defaults={"rating": grade}
        )

        average_rating = UserRating.objects.filter(rated_user_id=user_id).aggregate(
            Avg("rating")
        )["rating__avg"]

        if average_rating is None:
            average_rating = 0

        return JsonResponse({"average_rating": average_rating})
    except (ValueError, UserRating.DoesNotExist):
        return JsonResponse({"message": "Ошибка обработки запроса"}, status=400)


def notification_list(request):
    user = request.user
    notifications = Message.objects.filter(recipients=user).order_by("-created_at")
    with transaction.atomic():
        for notification in notifications:
            if not notification.is_read:
                notification.is_read = True
                notification.save()
    return render(request, "user/notification.html", {"notifications": notifications})


class SendNotificationView(View):
    template_name = "user/send-message.html"

    def get(self, request):
        form = NotificationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = NotificationForm(request.POST)
        if form.is_valid():
            message_text = form.cleaned_data["message"]
            send_to_all = form.cleaned_data["send_to_all"]
            filtered_users = form.cleaned_data.get("filtered_users")
            category = form.cleaned_data.get("category")
            subcategory = form.cleaned_data.get("subcategory")
            tags = form.cleaned_data.get("tags")
            User = get_user_model()
            users = []
            if send_to_all:
                users = User.objects.all()
            elif filtered_users:
                users = filtered_users
            elif category or subcategory or tags:
                # Фильтрация пользователей на основе выбранной категории, подкатегории и меток
                users = User.objects.filter(
                    companyprofile__category=category,
                    companyprofile__sub_category=subcategory,
                    companyprofile__tags__in=tags,
                ).distinct()

            for user in users:
                # Создаем сообщение для каждого пользователя в списке получателей
                message = Message.objects.create(
                    sender=request.user,  # Отправитель текущий пользователь
                    message=message_text,
                )
                message.recipients.add(user)  # Добавляем получателей к сообщению
            messages.success(request, "Вы успешно отправили сообщение")
            return redirect("notification")

        return render(request, self.template_name, {"form": form})


def product_phone_view_count(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        session_key = "product_{}_viewed".format(product_id)

        # Check if the product has already been viewed by the user
        if not request.session.get(session_key, False):
            try:
                product = Products.objects.get(pk=product_id)
                product.telephone_view_count += 1
                product.save()
                # Mark the product as viewed in the user's session
                # request.session[session_key] = True

                return JsonResponse({"status": "success"})
            except Products.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Product not found"})

        # Product has already been viewed, return an error
        return JsonResponse({"status": "error", "message": "Product already viewed"})

    return JsonResponse({"status": "error", "message": "Invalid request method"})


class SendUserDataView(View):
    def get(self, request):
        return render(request, "./user/sections/forgot-password.html")

    def post(self, request):
        email = request.POST["email"]
        if email:
            user = get_user_model()
            if user.objects.get(email=email) is not None:
                verify_code = generate_password()
                request.session["verification_code"] = verify_code
                try:
                    send_mail(
                        "Ibroxim",
                        f"vertify code: {verify_code}",
                        settings.EMAIL_HOST_USER,
                        [email],
                    )
                    messages.success(request, "Emailga code jo'natildi")
                    return render(request, "./user/sections/update-password.html")
                except:
                    messages.error(request, "Проблемы отправкой сообщение")
                    return redirect("forgot-password")


def update_password(request):
    email = request.POST["email"]
    verification_code = request.POST["verification_code"]
    new_password = request.POST["new_password"]
    if email and verification_code and new_password:
        user = get_user_model()
        stored_verification_code = request.session.get("verification_code")
        try:
            # Verify the verification code (You should implement your verification logic)
            if stored_verification_code == verification_code:
                user_instance = user.objects.get(email=email)
                # Set the new password (You may want to use Django's make_password function)
                user_instance.password = make_password(new_password)
                user_instance.save()
                messages.success(
                    request,
                    "Сброс пароля успешен. Теперь вы можете войти в систему с новым паролем.",
                )
                return redirect("login")
            else:
                messages.error(
                    request,
                    "Неверный код подтверждения. Пожалуйста, попробуйте еще раз.",
                )
                return render(request, "./user/sections/update-password.html")
        except user.DoesNotExist:
            messages.error(
                request,
                "Пользователь не найден. Введите, пожалуйста, действительный адрес электронной почты.",
            )
            return redirect("forgot-password")


"""

Client ID: 1064949093248-47olpbv7o9ruglkk9g46ojcqhp1b12ev.apps.googleusercontent.com

Client secret: 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

"""


# @login_required
# def subscribe(request, user_id):
#     target_user = get_object_or_404(get_user_model(), pk=user_id)
#
#     # Проверка, чтобы пользователь не мог подписаться на самого себя
#     if request.user == target_user:
#         return JsonResponse({'error': 'Вы не можете подписаться на себя.'}, status=400)
#
#     subscription, created = UserSubscription.objects.get_or_create(subscriber=request.user, target_user=target_user)
#
#     if not created:
#         # Если уже подписаны, отписываемся
#         subscription.delete()
#
#     return JsonResponse({'subscribed': created})

# Добавьте URL-паттерн в ваш urls.py
# path('subscribe/<int:user_id>/', views.subscribe, name='subscribe')


@login_required
def subscribe(request, user_id):
    target_user = get_object_or_404(get_user_model(), pk=user_id)
    if request.user == target_user:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    subscription, created = UserSubscription.objects.get_or_create(
        subscriber=request.user, target_user=target_user
    )

    if not created:
        subscription.delete()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def complaint_view(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST)
        report_from_this = request.user
        report_to_user = request.POST.get("profile-pk")
        # complaint_type =
        # description =
        if form.is_valid():
            complaint = Complaint(
                complaint_type=form.cleaned_data["complaint_type"],
                description=form.cleaned_data["description"],
                sender=report_from_this,
                recipient=get_object_or_404(get_user_model(), pk=report_to_user),
            )
            complaint.save()
            message = Message.objects.create(
                sender=report_from_this,
                message=f"Вам пришел жалоба|  {form.cleaned_data['complaint_type']} --- {form.cleaned_data['description']}",
                created_at=timezone.now(),
            )

            message.recipients.set([report_to_user])
            messages.success(
                request,
                "Жалоба успешно отправлено, мы в скором времене проверим этого пользователя",
            )
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
        else:
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


def is_admin(user):
    return user.is_superuser or user.is_staff


@user_passes_test(
    is_admin, login_url=None
)  # Укажите нужный URL для редиректа в случае отсутствия прав доступа
def admin_dashboard_view(request):
    context = {
        # "films_in_pending": films,
    }

    return render(request, "admin/dashboard.html", context)


class AdminUserListView(ListView):
    model = get_user_model()
    template_name = "admin/list-accounts.html"
    context_object_name = "users"

    def get_queryset(self):
        return self.model.objects.filter(
            Q(is_business_account=None) | Q(is_business_account=True), is_active=True
        )

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")
        user = get_object_or_404(get_user_model(), pk=user_id)

        if action == "delete":
            user.is_active = False
        elif action == "deactivate":
            user.is_business_account = False
        user.save()
        return self.get(request, *args, **kwargs)


class AdminUserVerify(ListView):
    model = get_user_model()
    template_name = "admin/user-verify.html"
    context_object_name = "verify_accounts"

    def get_queryset(self):
        return get_user_model().objects.filter(is_business_account=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        user_id = self.request.POST.get("user_id")
        if user_id:
            user = get_object_or_404(get_user_model(), pk=user_id)
            user.is_business_account = True
            user.save()
            return redirect("admin_user_verify")


class AdminUserDeleted(ListView):
    model = get_user_model()
    template_name = "admin/user-deleted.html"
    context_object_name = "accounts"

    def get_queryset(self):
        return get_user_model().objects.filter(is_active=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        user_id = self.request.POST.get("user_id")
        if user_id:
            user = get_object_or_404(get_user_model(), pk=user_id)
            user.is_active = True
            user.save()
            return redirect("admin_user_deleted")


class AdminProductsActive(ListView):
    model = Products
    template_name = "admin/products_active.html"
    context_object_name = "products"

    def get_queryset(self, *args, **kwargs):
        return Products.objects.filter(is_active=True).order_by("-create_date")

    def post(self, *args, **kwargs):
        action, product_id = self.request.POST.get("action").split()
        product = get_object_or_404(self.model, id=product_id)
        # if action == "deactive":
        #     product.
        if action == "delete":
            product.delete()
        elif action == "update":
            ...
        elif action == "deactive":
            product.is_active = False
        product.save()
        return redirect("admin_user_products_active")


class AdminProductsModeration(ListView):
    model = Products
    template_name = "admin/products_moderation.html"
    context_object_name = "products"

    def get_queryset(self):
        return Products.objects.filter(is_active=False).order_by("-create_date")

    def post(self, *args, **kwargs):
        action, product_id = self.request.POST.get("action").split()
        product = get_object_or_404(self.model, id=product_id)
        product.is_active = True
        product.save()
        return redirect("admin_user_products_moderation")


class AdminStatistics(View):
    template_name = "admin/admin_statistics.html"

    def get(self, *args, **kwargs):
        context = {
            "statistic_balls": PointsTransaction.objects.filter(
                transaction_type="purchase"
            ).order_by("-timestamp")
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        filter_statistics = self.request.POST.get("filter")
        statistics = PointsTransaction.objects.filter(
            transaction_type="purchase",
        )
        if filter_statistics == "today":
            statistics = statistics.filter(
                timestamp__date=datetime.today().date(),
            )

        elif filter_statistics == "1 week":
            seven_days_ago = datetime.today() - timedelta(days=7)
            statistics = statistics.filter(
                timestamp__date__gte=seven_days_ago.date(),
            )

        elif filter_statistics == "1 month":
            first_day_of_month = datetime.today().replace(day=1)
            statistics = statistics.filter(
                timestamp__date__gte=first_day_of_month.date(),
            )

        context = {"statistic_balls": statistics.order_by("-timestamp")}
        return render(self.request, self.template_name, context)


class SupportView(ListView):
    model = SupportTicket
    template_name = "admin/admin_support.html"
    context_object_name = "messages"

    def get_queryset(self):
        return self.model.objects.filter(checked=False).order_by("-created_at")


def add_ball(request, user_id):
    user = get_user_model().objects.get(pk=user_id)

    if request.method == "POST":
        form = AddBallForm(request.POST)
        if form.is_valid():
            ball_amount = form.cleaned_data["ball_amount"]
            user.ball += ball_amount
            user.save()
            return redirect("admin_user_list")
    else:
        form = AddBallForm()

    return render(request, "admin/add_ball.html", {"form": form})


class TopUpYourAccount(View):
    template_name = "user/add-ball.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"form": TopUpYourAccountForm()})

    def post(self, request, *args, **kwargs):
        amount = self.request.POST.get("amount")
        photo = self.request.FILES.get("photo")
        asyncio.run(send_message(self.request.user.pk, amount, photo))
        return redirect('myaccount')
