"""
Django management команда для автоматичного створення суперюзера
Використовується при деплої на Render
Безпечна для багаторазового запуску (idempotent)

Створює суперюзера тільки якщо його ще не існує.
Логін та пароль беруться з змінних середовища або використовують дефолтні значення.

ENV змінні:
- DJANGO_SUPERUSER_USERNAME (дефолт: Sofia)
- DJANGO_SUPERUSER_PASSWORD (дефолт: 3002Luna)
- DJANGO_SUPERUSER_EMAIL (дефолт: sofia@prometey.com)
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Створює суперюзера якщо він ще не існує (idempotent)'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Отримуємо дані з ENV або використовуємо дефолтні значення
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'Sofia')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '3002Luna')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'sofia@prometey.com')
        
        # Перевіряємо чи суперюзер вже існує
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'⚠️  Суперюзер "{username}" вже існує, пропускаємо створення')
            )
            return
        
        # Створюємо суперюзера
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Суперюзер "{username}" успішно створений!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Помилка при створенні суперюзера: {e}')
            )
            raise

