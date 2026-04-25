from .models import Post, Category
from modeltranslation.translator import TranslationOptions,register

@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'text')

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', )