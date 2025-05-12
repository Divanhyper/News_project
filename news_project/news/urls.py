# homepage/urls.py

# Импортируем функцию path()
# и файл homepage/views.py, в котором объявлена view-функция index().
from django.urls import path
from django.conf import settings   # ← Обязательно!
from django.conf.urls.static import static      # ← Обязательно!

from . import views

app_name = 'news'

urlpatterns = [
    # Если вызван URL без относительного адреса (шаблон — пустые кавычки),
    # то вызывается view-функция index() из файла views.py
    path('', views.IndexView.as_view(), name='index'),
    path('news/', views.ArticleListView.as_view(), name='post_list'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='post_detail'),
    path('category/<slug:slug>/',views.CategoryDetailView.as_view(),name='category_detail'),
    path('404/', views.er404, name='er404'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)