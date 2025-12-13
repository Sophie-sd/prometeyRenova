"""
Django management команда для оновлення дат існуючих статей на 2025 рік
Розподіляє дати рівномірно по всьому року
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from apps.blog.models import BlogPost


class Command(BaseCommand):
    help = 'Оновлює дати всіх опублікованих статей на 2025 рік'

    def handle(self, *args, **options):
        # Отримуємо всі опубліковані статті, відсортовані за ID
        posts = BlogPost.objects.filter(is_published=True).order_by('id')
        total_posts = posts.count()
        
        if total_posts == 0:
            self.stdout.write(self.style.WARNING('⚠️  Немає статей для оновлення'))
            return
        
        # Генеруємо дати рівномірно по 2025 року
        # Розподіляємо дати від 1 січня до 31 грудня
        dates_2025 = []
        for i in range(total_posts):
            # Розраховуємо день року (1-365)
            day_of_year = int((i / total_posts) * 364) + 1
            # Конвертуємо номер дня в дату
            date = timezone.make_aware(datetime(2025, 1, 1)) + timezone.timedelta(days=day_of_year - 1)
            dates_2025.append(date)
        
        # Оновлюємо дати для кожної статті
        updated_count = 0
        for idx, post in enumerate(posts):
            if idx < len(dates_2025):
                post.created_at = dates_2025[idx]
                post.save(update_fields=['created_at'])
                updated_count += 1
                self.stdout.write(f'  ✅ Оновлено: {post.title} → {post.created_at.strftime("%d.%m.%Y")}')
        
        self.stdout.write(self.style.SUCCESS(f'✨ Оновлено {updated_count} статей'))

