from django.contrib import admin
from .models import Category, Post, PostCategory, Author
from modeltranslation.admin import TranslationAdmin




class PostCategoryInline(admin.TabularInline):
    model = PostCategory
    extra = 1


class PostAdmin(TranslationAdmin, admin.ModelAdmin):
    model = Post
    inlines = [PostCategoryInline]
    list_display = ('title', 'posted_by__user__username')
    list_filter = ('post_category', 'posted_by__user__username')
    search_fields = ('title', 'post_category__name')


class CategoryAdmin(TranslationAdmin, admin.ModelAdmin):
    model = Category
    list_display = ('name', 'subs_amount', 'posts_in_category')
    list_filter = ('name', )
    search_fields = ('name', )


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user__username', 'posts_amount', 'rating')
    list_filter = ('user__username', )
    search_fields = ('user__username', )






admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Author, AuthorAdmin)
