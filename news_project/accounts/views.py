from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView

from .forms import RegistrationForm, UserLoginForm, ProfileForm, ProfileAndUserForm
from news.models import Profile, Comment

User = get_user_model()

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/signin.html'

class UserRegisterView(CreateView):
    form_class = RegistrationForm
    template_name = 'accounts/signin.html'
    success_url = reverse_lazy('news:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        # self.object is the newly created User
        login(self.request, self.object)
        return response

class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        # form.get_user() вернёт объект User, если пароль верный
        user = form.get_user()
        # «прописать» пользователя в сессии
        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        # при невалидных данных форма сама покажет ошибки
        return super().form_invalid(form)

class UserLogoutView(LogoutView):
    # Куда редиректить после logout
    next_page = reverse_lazy('accounts:user_login')
    # Разрешаем GET‑запросы (по умолчанию только POST и OPTIONS)
    http_method_names = ['get', 'post', 'options']

    def get(self, request, *args, **kwargs):
        # Обрабатываем GET точно так же, как POST
        return self.post(request, *args, **kwargs)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileAndUserForm
    template_name = 'accounts/profile-edit.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        # правим только свой профиль
        return self.request.user.profile

    def get_success_url(self):
        return reverse('accounts:user_profile', kwargs={
            'username': self.request.user.username
        })

class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'accounts/profile-details.html'
    context_object_name = 'profile'

    def get_object(self):
        username = self.kwargs.get('username')
        print("Получен username:", username)
        user = get_object_or_404(User, username=username)
        return get_object_or_404(Profile, user=user)


class CustomPasswordResetView(PasswordResetView):
    template_name            = 'accounts/forgot-password.html'
'''
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url   = reverse_lazy('accounts:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'''