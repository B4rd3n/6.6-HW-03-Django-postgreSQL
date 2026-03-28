from django.urls import path
from .views import NewsList, NewsDetailView, SearchNews, CreateArticles, CreateNews, UpdateArticles, UpdateNews, \
    DeleteNews, DeleteArticles

urlpatterns = [
    path('', NewsList.as_view(), name='news_list'),
    path('<int:pk>', NewsDetailView.as_view(), name='news_detail'),
    path('search/', SearchNews.as_view(), name='news_search'),
    path('articles/create/', CreateArticles.as_view(), name='articles_create'),
    path('create/', CreateNews.as_view(), name='news_create'),
    path('articles/<int:pk>/edit/', UpdateArticles.as_view(), name='articles_edit'),
    path('<int:pk>/edit/', UpdateNews.as_view(), name='news_edit'),
    path('articles/<int:pk>/delete/', DeleteArticles.as_view(), name='articles_delete'),
    path('<int:pk>/delete/', DeleteNews.as_view(), name='news_delete'),
]
