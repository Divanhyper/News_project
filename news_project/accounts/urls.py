# Импортируем функцию path()
# и файл homepage/views.py, в котором объявлена view-функция index().
from django.urls import path
from django.contrib.auth.views import (
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from . import views
from django.conf import settings   # ← Обязательно!
from django.conf.urls.static import static      # ← Обязательно!


app_name = 'accounts'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('signup/', views.UserRegisterView.as_view(), name='user_signup'),
    path('logout/', views.UserLogoutView.as_view(), name='user_logout'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='user_profile_edit'),
    path('profile/<str:username>/', views.ProfileDetailView.as_view(), name='user_profile'),
    path('reset_password/', views.CustomPasswordResetView.as_view(), name='user_reset'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)