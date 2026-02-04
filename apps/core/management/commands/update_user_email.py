"""
Django management команда для оновлення email користувача (особливо корисно для суперюзера)
Використовується при деплої на Render або вручну для оновлення email без доступу до адмінки

ENV змінні:
- DJANGO_USER_USERNAME (користувач для оновлення)
- DJANGO_USER_EMAIL (новий email)

Приклад:
    python manage.py update_user_email --username Sofia --email new_sofia@example.com
    або через ENV:
    DJANGO_USER_USERNAME=Sofia DJANGO_USER_EMAIL=new_sofia@example.com python manage.py update_user_email
"""
import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Оновлює email користувача. Корисно для суперюзера коли немає доступу до адмінки.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username користувача для оновлення'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Новий email'
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Отримуємо дані з аргументів або ENV
        username = options.get('username') or os.environ.get('DJANGO_USER_USERNAME')
        email = options.get('email') or os.environ.get('DJANGO_USER_EMAIL')
        
        # Валідація
        if not username:
            raise CommandError(
                'Username не задано. Використовуйте --username або DJANGO_USER_USERNAME env.'
            )
        
        if not email:
            raise CommandError(
                'Email не задано. Використовуйте --email або DJANGO_USER_EMAIL env.'
            )
        
        # Перевіряємо чи користувач існує
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'Користувач "{username}" не знайдений.')
        
        # Оновлюємо email
        try:
            old_email = user.email
            user.email = email
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Email користувача "{username}" успішно оновлено:\n'
                    f'   Старий email: {old_email}\n'
                    f'   Новий email: {email}'
                )
            )
        except Exception as e:
            raise CommandError(f'❌ Помилка при оновленні email: {e}')
