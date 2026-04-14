from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.core.cache import cache

from .content_types import POSITIONS



class Author(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    rating = models.FloatField(default = 0)

    def update_rating(self):
        post_rating = Post.objects.filter(posted_by = self).aggregate(total = Sum('rating'))['total'] or 0
        post_rating *= 3
        authors_comments = Comment.objects.filter(commentator = self.user).aggregate(total = Sum('rating'))['total'] or 0
        post_comments = Comment.objects.filter(post__posted_by = self).aggregate(total = Sum('rating'))['total'] or 0


        self.rating = post_rating + authors_comments + post_comments
        self.save()

    def __str__(self):
        return self.user.username




class Category(models.Model):
    name = models.CharField(max_length = 255, unique = True)
    sub = models.ManyToManyField(User, through="Subscriber", related_name="subscribed_categories")

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length = 255)
    text = models.TextField()
    rating = models.FloatField(default = 0)
    content_type = models.CharField(max_length=2, choices=POSITIONS)
    creation_time = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey("Author", on_delete = models.CASCADE)
    is_notified = models.BooleanField(default=False)

    post_category = models.ManyToManyField("Category", through = "PostCategory")

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        preview_text = self.text[:124] + "..." if len(self.text) > 124 else self.text
        return preview_text

    def get_absolute_url(self):
        return reverse('news_detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.title.title()}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'post-{self.pk}')



class PostCategory(models.Model):
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    post = models.ForeignKey(Post, on_delete = models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    commentator = models.ForeignKey(User, on_delete = models.CASCADE)
    text = models.TextField()
    creation_time = models.DateTimeField(auto_now_add = True)
    rating = models.FloatField(default = 0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

class Subscriber(models.Model):
    user_sub = models.ForeignKey(User, on_delete = models.CASCADE)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)


    def get_absolute_url(self):
        return reverse('news_list')


