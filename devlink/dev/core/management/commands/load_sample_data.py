from django.core.management.base import BaseCommand
from core.models import Category, Tag

class Command(BaseCommand):
    help = 'Loads sample categories and tags'

    def handle(self, *args, **options):
        categories = [
            'Programming Languages',
            'Frameworks',
            'Tools',
            'Databases',
            'DevOps'
        ]

        tags = [
            'python', 'javascript', 'django', 'react', 
            'docker', 'git', 'aws', 'postgresql', 'beginners'
        ]

        for cat in categories:
            Category.objects.get_or_create(name=cat, slug=cat.lower().replace(' ', '-'))

        for tag in tags:
            Tag.objects.get_or_create(name=tag, slug=tag.lower())

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data'))
        