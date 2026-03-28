from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .filters import PostFilter
from .forms import PostForm

from .models import Post


class NewsList(ListView):
    model = Post
    ordering = '-creation_time'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    filterset = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs


class NewsDetailView(DetailView):
    model = Post
    template_name = 'single_news.html'
    context_object_name = 'single_news'


class SearchNews(NewsList):
    template_name = 'search_news.html'


class CreateContent(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'edit_article_and_news.html'
    type_of_content = ''

    def form_valid(self, form):
        article = form.save(commit=False)
        article.content_type = self.type_of_content
        return super().form_valid(form)


class CreateArticles(CreateContent):
    type_of_content = 'AT'


class CreateNews(CreateContent):
    type_of_content = 'NW'


class UpdateContent(UpdateView):
    form_class = PostForm
    model = Post
    template_name = ''
    type_of_content = ''

    def get_queryset(self):
        return Post.objects.filter(content_type = self.type_of_content)


class UpdateArticles(UpdateContent):
    template_name = 'edit_article_and_news.html'
    type_of_content = 'AT'



class UpdateNews(UpdateContent):
    template_name = 'edit_article_and_news.html'
    type_of_content = 'NW'


class DeleteContent(DeleteView):
    model = Post
    template_name = ''
    type_of_content = ''
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(content_type = self.type_of_content)


class DeleteArticles(DeleteContent):
    template_name = 'delete_article_and_news.html'
    type_of_content = 'AT'


class DeleteNews(DeleteContent):
    template_name = 'delete_article_and_news.html'
    type_of_content = 'NW'





