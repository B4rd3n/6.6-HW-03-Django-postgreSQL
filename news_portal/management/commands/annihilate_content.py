from django.core.management.base import BaseCommand, CommandError
from ...models import Post, Category

class Command(BaseCommand):
    help = 'Some kind of hint'
    missing_args_message = 'Please provide some arguments'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('category_id', nargs="+", type=int)


    def handle(self, *args, **options):
        delete_category = Category.objects.filter(pk__in=options['category_id'])
        if len(delete_category) != len(options['category_id']):
            raise CommandError("Please, provide valid categories")
        self.stdout.readable()
        self.stdout.write(f'Ary you sure you want to delete all posts from these categories "{", ".join(cat.get("name") for cat in list(delete_category.values("name")))}"? yes/no')

        answer = input()
        if answer == 'yes':
            Post.objects.filter(post_category__in=delete_category).delete()
            self.stdout.write(f'Deleted successfully')
            return
        self.stdout.write(self.style.ERROR('Access denied'))


