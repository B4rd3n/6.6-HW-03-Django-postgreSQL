from django.urls import path, include
from api import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'news', views.NewsViewSet, basename='news')
router.register(r'articles', views.ArticlesViewSet, basename='articles')

urlpatterns = [
    path('', include(router.urls)),
]
