"""
Django management команда для автоматичного створення суперюзера
Використовується при деплої на Render
Безпечна для багаторазового запуску (idempotent)

Створює суперюзера тільки якщо його ще не існує.
Логін та пароль беруться з змінних середовища.

ENV змінні (ОБОВ'ЯЗКОВІ на production):
- DJANGO_SUPERUSER_USERNAME (дефолт локально: Sofia)
- DJANGO_SUPERUSER_PASSWORD (ОБОВ'ЯЗКОВИЙ на production, дефолту немає!)
- DJANGO_SUPERUSER_EMAIL (дефолт локально: sofia@prometey.com)

ВАЖЛИВО: На production (DEBUG=False) пароль МУСИТЬ бути задано через ENV.
          Без пароля команда не створюватиме суперюзера.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings


class Command(BaseCommand):
    help = 'Створює суперюзера якщо він ще не існує (idempotent, безпечно)'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Отримуємо дані з ENV
        # На production дефолтів НЕМАЄ для пароля
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        
        # Для локальної розробки дозволяємо дефолти
        # Але на production ці значення беруться тільки з ENV
        if not settings.DEBUG:
            # PRODUCTION: дефолтів НЕМАЄ
            if not username:
                self.stdout.write(
                    self.style.WARNING(
                        '⚠️  На production DJANGO_SUPERUSER_USERNAME має бути задано в Render Environment'
                    )
                )
                return
            if not password:
                self.stdout.write(
                    self.style.ERROR(
                        '❌ На production DJANGO_SUPERUSER_PASSWORD ОБОВ\'ЯЗКОВО має бути задано в Render Environment (Secret).\n'
                        '   Без пароля суперюзер не буде створений для безпеки.'
                    )
                )
                return
            if not email:
                self.stdout.write(
                    self.style.WARNING(
                        '⚠️  На production DJANGO_SUPERUSER_EMAIL має бути задано в Render Environment'
                    )
                )
                return
        else:
            # ЛОКАЛЬНА РОЗРОБКА: дефолти дозволені
            username = username or 'Sofia'
            email = email or 'sofia@prometey.com'
            # Для пароля на локальній машині також дефолту НЕМАЄ!
            # Це допомагає уникнути небезпечних дефолтних паролів
            if not password:
                self.stdout.write(
                    self.style.WARNING(
                        '⚠️  DJANGO_SUPERUSER_PASSWORD не задано. Суперюзер не буде створений.\n'
                        '   Встановіть змінну середовища та спробуйте ще раз.'
                    )
                )
                return
        
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

