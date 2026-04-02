from django import forms

from .models import Post, Subscriber


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title',
                  'text',
                  'post_category']


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['category']
