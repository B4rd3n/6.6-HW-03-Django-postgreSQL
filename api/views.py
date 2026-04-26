from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions

from news_portal.models import Author
from api.serializers import PostSerializer, Post

class NewsViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(content_type='NW')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        author = Author.objects.get(user=self.request.user)
        serializer.save(posted_by=author)

class ArticlesViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(content_type='AT')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        author = Author.objects.get(user=self.request.user)
        serializer.save(posted_by=author)