import os
import django

# Указываем Django, где искать настройки
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'mysite.settings')  # Замените `your_project` на имя вашего проекта
django.setup()  # Загружаем настройки Django

from news.models import Article, Category, Tag
from django.core.files import File
from django.contrib.auth import get_user_model
from django.utils.text import slugify


# Теперь можно работать с моделями
def create_article():
    # Получаем модель пользователя
    User = get_user_model()

    # 1. Получаем необходимые объекты (автор, категория, теги)
    author = User.objects.get(username="divan")  # Пример: берём пользователя 'admin'
    category = Category.objects.get(slug='nature')  # Замените на реальный ID категории

    # 2. Создаем статью
    article = Article(
        title="Заголовок вашей статьи",
        slug=slugify("swagin"),  # Автоматически создаем slug из заголовка
        author=author,
        category=category,
        content="Текст вашей статьи...",
        status='published'  # или 'draft' для черновика
    )

    # 3. Добавляем изображение (если нужно)
    with open('media/media/article_img/red_bull.png', 'rb') as f:
        article.image.save('tested_red_bull.png', File(f), save=False)

    # 4. Сохраняем статью
    article.save()

if __name__ == "__main__":
    create_article()
    User = get_user_model()
    users = User.objects.all().values('id', 'username')  # или просто .all()

    for user in users:
        print(user['id'], user['username'])  # если использовали .values()
        # или print(user.id, user.username)  # если использовали .all()


