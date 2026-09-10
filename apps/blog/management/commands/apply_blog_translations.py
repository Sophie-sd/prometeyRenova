import json
import os
from django.core.management.base import BaseCommand
from apps.blog.models import BlogPost
from django.conf import settings

class Command(BaseCommand):
    help = 'Apply high-quality translations (RU, EN, CS) to all blog posts'

    def handle(self, *args, **options):
        json_path = os.path.join(settings.BASE_DIR, 'blog_translations_final.json')
        
        if not os.path.exists(json_path):
            self.stderr.write(self.style.ERROR(f'File not found: {json_path}'))
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)

        updated_count = 0
        for item in translations:
            try:
                post = BlogPost.objects.get(id=item['id'])
                post.title_ru = item['title_ru']
                post.title_en = item['title_en']
                post.title_cs = item['title_cs']
                post.excerpt_ru = item['excerpt_ru']
                post.excerpt_en = item['excerpt_en']
                post.excerpt_cs = item['excerpt_cs']
                post.content_ru = item['content_ru']
                post.content_en = item['content_en']
                post.content_cs = item['content_cs']
                post.keywords_ru = item['keywords_ru']
                post.keywords_en = item['keywords_en']
                post.keywords_cs = item['keywords_cs']
                post.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'Updated post ID {post.id}: {post.title}'))
            except BlogPost.DoesNotExist:
                self.stderr.write(self.style.WARNING(f'Post ID {item["id"]} not found'))

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} blog posts'))
