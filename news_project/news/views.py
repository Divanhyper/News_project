from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.views.generic.edit import FormMixin, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Count

from .forms import CommentForm
from .models import Article, Category, Tag, Comment


User = get_user_model()


class IndexView(TemplateView):
    template_name = 'news/index.html'

    def get_context_data(self, **kwargs):
        # сначала забираем базовый контекст
        context = super().get_context_data(**kwargs)
        latest_articles = Article.objects.filter(status='published').order_by('-created_at')[:5]
        # добавляем в него список опубликованных статей
        context['articles'] = latest_articles
        return context

class ArticleListView(ListView):
    model = Article
    paginate_by = 6
    template_name = 'news/post_grid.html'
    context_object_name = 'articles'
    queryset = Article.objects.filter(status='published')

    def get_queryset(self):
        return (
            Article.objects
            .filter(status='published')
            .annotate(comment_count=Count('comments'))
        )



class ArticleDetailView(FormMixin, DetailView):
    model = Article
    template_name = 'news/news-single.html'
    context_object_name = 'article'
    slug_field = 'slug'
    form_class = CommentForm

    def get_success_url(self):
        # остаёмся на той же статье
        return reverse('news:post_detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['comments'] = self.object.comments.filter(is_moderated=True)
        data.setdefault('form', self.get_form())
        return data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # передаём пользователя в форму, чтобы она могла убрать нужные поля
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # статья
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.article = self.object

        if self.request.user.is_authenticated:
            comment.user = self.request.user
            # подставляем их имя/почту
            comment.name = (
                self.request.user.get_full_name()
                or self.request.user.username
            )
            comment.email = self.request.user.email
        # иначе — в name/email уже то, что пришло из формы
        comment.save()
        return super().form_valid(form)


class CategoryDetailView(ListView):
    model = Article
    template_name = 'news/category_detail.html'
    context_object_name = 'articles'

    def get_queryset(self):
        # отбираем статьи по slug категории, переданному в URL
        return (
            Article.objects
                   .filter(status='published', category__slug=self.kwargs['slug'])
                   .annotate(comment_count=Count('comments'))
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['category'] = Category.objects.get(slug=self.kwargs['slug'])
        return ctx

class TagDetailView(DetailView):
    model = Tag
    template_name = 'news/tag_detail.html'
    context_object_name = 'tag'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'




class CommentDetailView(DetailView):
    model = Comment
    template_name = 'news/comment_detail.html'
    context_object_name = 'comment'
    pk_url_kwarg = 'pk'

def er404(request):
    template_name = 'news/404.html'
    raise Http404("Объект не найден")


