from rest_framework import serializers

from news_portal.models import Post

class PostSerializer(serializers.ModelSerializer):
    posted_by = serializers.ReadOnlyField(source='posted_by.username')


    class Meta:
        model = Post
        fields = ['title', 'text', 'posted_by', 'creation_time']
