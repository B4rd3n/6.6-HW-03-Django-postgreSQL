from allauth.core.internal.httpkit import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.http.response import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from datetime import datetime
from django.core.cache import cache
from django.utils import timezone
import logging
import pytz


from .filters import PostFilter
from .forms import PostForm, SubscribeForm
from .models import Post, Author, Subscriber, Category

# Тест логирования: Начало (http://127.0.0.1:8000/news/test-logs/)
logger = logging.getLogger('django')
security_logger = logging.getLogger('django.security')
db_logger = logging.getLogger('django.db.backends')

def test_logs(request):
    logger.debug("Test DEBUG: Here is the message in terminal!")
    logger.warning("Test WARNING: Path to file")

    try:
        1 / 0
    except ZeroDivisionError:
        logger.error("Test ERROR: Error stack!", exc_info=True)

    security_logger.info("Test SECURITY: Security Alert!")
    db_logger.error("Test DB: Database Alert!")

    return HttpResponse("Logs sent!")
# Тест логирования: Конец


class NewsList(ListView):
    model = Post
    ordering = '-creation_time'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10
    filterset = None


# Затестил создание своего слоя middleware.
    def get_template_names(self):
        if getattr(self.request, 'device_type', None) == 'mobile':
            print('Mobile')
        if getattr(self.request, 'device_type', None) == 'pc':
            print('Computer')
        else:
            print('Other')
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['timezones'] = pytz.common_timezones
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def post(self, request):
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('news_list')


class NewsDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'single_news.html'
    context_object_name = 'single_news'
    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'post-{self.kwargs["pk"]}', None)
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)
        return obj





class SearchNews(NewsList):
    template_name = 'search_news.html'


class CreateContent(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('news_portal.add_post',)

    form_class = PostForm
    model = Post
    template_name = 'edit_article_and_news.html'
    type_of_content = ''

    def form_valid(self, form):
        author = Author.objects.get(user=self.request.user)

        today = datetime.now().date()
        posts_count = Post.objects.filter(posted_by=author, creation_time__date=today).count()

        if posts_count >= 3:
            form.add_error(None, "You can't publish more than three posts per day")
            return self.form_invalid(form)



        article = form.save(commit=False)
        article.content_type = self.type_of_content
        article.posted_by = Author.objects.get(user=self.request.user)

        article.save()
        form.save_m2m()

        return super().form_valid(form)


class CreateArticles(CreateContent):
    type_of_content = 'AT'


class CreateNews(CreateContent):
    type_of_content = 'NW'


class UpdateContent(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, UpdateView):
    permission_required = ('news_portal.add_post',)

    form_class = PostForm
    model = Post
    template_name = ''
    type_of_content = ''

    def get_queryset(self):
        return Post.objects.filter(content_type = self.type_of_content)

    def test_func(self):
        post_obj = self.get_object()
        return post_obj.posted_by.user == self.request.user


class UpdateArticles(UpdateContent):
    template_name = 'edit_article_and_news.html'
    type_of_content = 'AT'


class UpdateNews(UpdateContent):
    template_name = 'edit_article_and_news.html'
    type_of_content = 'NW'


class DeleteContent(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, DeleteView):
    permission_required = ('news_portal.add_post',)

    model = Post
    template_name = ''
    type_of_content = ''
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(content_type = self.type_of_content)

    def test_func(self):
        post_obj = self.get_object()
        return post_obj.posted_by.user == self.request.user


class DeleteArticles(DeleteContent):
    template_name = 'delete_article_and_news.html'
    type_of_content = 'AT'


class DeleteNews(DeleteContent):
    template_name = 'delete_article_and_news.html'
    type_of_content = 'NW'


class BecomeAuthor(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'become_author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context

    def test_func(self):
        is_author = self.request.user.groups.filter(name='authors').exists()
        return not is_author


class Subscriptions(LoginRequiredMixin, CreateView):
    form_class = SubscribeForm
    model = Subscriber
    template_name = 'subscriptions.html'
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        subscribed = Subscriber.objects.filter(user_sub=user).values_list('category_id', flat=True)
        form.fields.get('category').queryset = Category.objects.exclude(id__in=subscribed)
        return form


    def form_valid(self, form):
        subscriber = form.save(commit=False)
        subscriber.user_sub = self.request.user
        subscriber.save()
        return super().form_valid(form)




