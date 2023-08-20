from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetCompleteView
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.views import generic
from config import settings
from users.forms import UserForm, UserRegisterForm, PasswordResetConfirmForm, CustomPasswordResetForm
from users.models import User
from users.services.email_send_verify import send_mail_for_verify


class ProfileUpdateView(generic.UpdateView):
    """Представление для изменения данных пользователя"""
    model = User
    form_class = UserForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class RegisterView(generic.CreateView):
    """Представление для регистрации пользователя"""
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:confirm_email')

    def form_valid(self, form):
        """Отправка сообщения для верификации"""
        response = super().form_valid(form)
        user = form.save()
        # отправка сообщения для подтверждения электронной почты
        send_mail_for_verify(self.request, user)
        return response


class EmailVerify(generic.View):
    """Представление для верификации"""

    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)

        # проверка что токен сброса пароля верен для данного пользователя
        if user is not None and default_token_generator.check_token(user, token):
            user.save()
            login(request, user)
            return redirect('users:login')
        return redirect('users:invalid_verify')

    @staticmethod
    def get_user(uidb64):
        """Получение пользователя по uid"""
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user


class CustomPasswordResetView(PasswordResetView):
    """Восстановление пароля"""
    template_name = 'users/password_reset_form.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('users:password_reset_done')
    title = "Сброс пароля для Skychimp"
    email_template_name = 'users/email_reset.html'
    from_email = settings.EMAIL_HOST_USER


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Подтверждение сброса пароля"""
    form_class = PasswordResetConfirmForm
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Выполнение сброса пароля"""
    template_name = 'users/password_reset_done.html'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'blog/blog_list.html'
