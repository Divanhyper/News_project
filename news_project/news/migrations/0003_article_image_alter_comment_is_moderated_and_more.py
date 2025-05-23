# Generated by Django 5.2 on 2025-05-11 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_comment_email_comment_name_alter_comment_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='image',
            field=models.ImageField(help_text='Загрузите изображение для статьи', null=True, upload_to='media/article_img/', verbose_name='Изображение статьи'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='is_moderated',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, default='avatars/ava2.webp', null=True, upload_to='avatars'),
        ),
    ]
