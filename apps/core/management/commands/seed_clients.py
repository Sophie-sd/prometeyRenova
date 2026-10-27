"""
Ідемпотентне наповнення стрічки «Наші клієнти» з apps/core/home_clients_data.py.

Запускається з build.sh і scripts/start.sh. Для кожного клієнта зі списку
оновлює site_url, logo_static, order і вмикає показ. Записи не зі списку без
site_url (старі 9 лого до 27.10.2026) приховує (is_active=False) — без видалення.
Адмінський аплоад `logo` не чіпає, крім лого, яке колись поклав старий seed.
"""
import re
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.core.home_clients_data import HOME_CLIENTS
from apps.core.models import Client

# Файли, які старий seed копіював у media/clients/ зі static/images/portfolio/*.png
# (Django міг додати суфікс _AbC1234). Такі лого не мають перекривати нові static.
LEGACY_SEED_LOGO_STEMS = {
    'speakup', 'coresync', 'playvision', 'beautyshop', 'redrabbit',
    'adiabatic', 'polygraph', 'pulvas_store', 'airinua',
}
_DJANGO_SUFFIX = re.compile(r'_[A-Za-z0-9]{7}$')


def is_legacy_seed_logo(name: str) -> bool:
    if not name:
        return False
    stem = _DJANGO_SUFFIX.sub('', Path(name).stem)
    return stem in LEGACY_SEED_LOGO_STEMS


class Command(BaseCommand):
    help = 'Створює/оновлює клієнтів стрічки «Наші клієнти» і приховує застарілі'

    def handle(self, *args, **options):
        created = updated = 0
        listed_names = set()

        for item in HOME_CLIENTS:
            name = item['name'].strip()
            listed_names.add(name)
            values = {
                'site_url': item['site_url'],
                'logo_static': item['logo_static'],
                'order': item['order'],
                'is_active': True,
            }
            client, was_created = Client.objects.get_or_create(name=name, defaults=values)
            if was_created:
                created += 1
                continue
            for key, value in values.items():
                setattr(client, key, value)
            if is_legacy_seed_logo(client.logo.name):
                client.logo = ''
            client.save()
            updated += 1

        hidden = (
            Client.objects.exclude(name__in=listed_names)
            .filter(site_url='', is_active=True)
            .update(is_active=False)
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Клієнти: створено {created}, оновлено {updated}, приховано {hidden}, '
                f'активних {Client.objects.filter(is_active=True).count()}.'
            )
        )
