from io import BytesIO

from PIL import Image, ImageDraw
from django.core.files.base import ContentFile
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth import get_user_model


user = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tag_detail', kwargs={'slug': self.slug})


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars', default='avatars/ava2.webp', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.avatar:
            img = Image.open(self.avatar.path).convert("RGBA")

            # Обрезаем до квадрата
            size = min(img.width, img.height)
            left = (img.width - size) // 2
            top  = (img.height - size) // 2
            img = img.crop((left, top, left + size, top + size))

            # Ресайзим с LANCZOS
            img = img.resize((150, 150), Image.Resampling.LANCZOS)

            # Делаем круговую маску
            mask = Image.new('L', (150, 150), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 150, 150), fill=255)

            # Накладываем маску
            result = Image.new('RGBA', (150, 150))
            result.paste(img, (0, 0), mask=mask)

            # Сохраняем как PNG (чтобы сохранить прозрачность)
            buffer = BytesIO()
            result.save(buffer, format='PNG')
            self.avatar.save(
                self.avatar.name,
                ContentFile(buffer.getvalue()),
                save=False
            )
            buffer.close()

            super().save(*args, **kwargs)

    def __str__(self):
        return f"Profile of {self.user.username}"

    def get_absolute_url(self):
        return reverse('accounts:user_profile', kwargs={'username': self.user.username})


class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles')
    image = models.ImageField(
        upload_to='media/article_img/',  # папка для загрузки изображений
        verbose_name='Изображение статьи',
        null=True,
        help_text='Загрузите изображение для статьи'
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles')
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    def save(self, *args, **kwargs):
        # сперва сохраняем, чтобы получить self.image.path
        super().save(*args, **kwargs)

        if self.image:
            img_path = self.image.path
            img = Image.open(img_path)
            # задаём нужное соотношение
            target_ratio = 16 / 9
            width, height = img.size
            current_ratio = width / height

            if current_ratio > target_ratio:
                # слишком широкое — обрезаем по ширине
                new_width = int(target_ratio * height)
                left = (width - new_width) // 2
                crop_box = (left, 0, left + new_width, height)
            else:
                # слишком высокое — обрезаем по высоте
                new_height = int(width / target_ratio)
                top = (height - new_height) // 2
                crop_box = (0, top, width, top + new_height)

            cropped = img.crop(crop_box)
            resized = cropped.resize((800, 450), Image.ANTIALIAS)  # пример размера

            # сохраняем в тот же файл
            buffer = BytesIO()
            resized.save(buffer, format=img.format)
            self.image.save(self.image.name, ContentFile(buffer.getvalue()), save=False)
            buffer.close()

            # и ещё раз сохраняем модель, чтобы записать новый файл
            super().save(*args, **kwargs)


    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at'])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments', null=True,
                             blank=True)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_moderated = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"

    def get_absolute_url(self):
        # Could point to article detail with anchor to this comment
        return f"{self.article.get_absolute_url()}#comment-{self.id}"
