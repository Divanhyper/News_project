from django.contrib import admin
from .models import Article, Category, Tag, Comment, Profile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'user__email')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at')
    list_filter = ('status', 'category', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    raw_id_fields = ('author',)
    filter_horizontal = ('tags',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('short_content', 'user', 'article', 'is_moderated', 'created_at')
    list_filter = ('is_moderated', 'created_at')
    search_fields = ('content', 'user__username', 'article__title')
    actions = ['approve_comments']

    def short_content(self, obj):
        return obj.content[:50]

    short_content.short_description = 'Content'

    def approve_comments(self, request, queryset):
        queryset.update(is_moderated=True)

    approve_comments.short_description = 'Approve selected comments'


