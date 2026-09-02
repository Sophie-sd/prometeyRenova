"""
Management command: seed_feature_blocks

Створює 3 feature-блоки для сторінки /portfolio-beta/.
Запускати лише один раз або при порожній таблиці.
"""
from django.core.management.base import BaseCommand

from apps.core.i18n_content import translate_ua_to_ru
from apps.core.models import PortfolioFeatureBlock


BLOCKS = [
    {
        'order': 0,
        'title': 'Українська адмінпанель — без зайвого',
        'text': (
            'Перша і єдина в Україні повністю україномовна адміністративна панель '
            'для керування сайтом. Жодних Google Translate, жодних незрозумілих пунктів — '
            'тільки чітка, зрозуміла мова. Ви вносите зміни в контент самостійно, '
            'без залучення розробника.'
        ),
    },
    {
        'order': 1,
        'title': 'Персоналізована під ваш бізнес',
        'text': (
            'Кожна адмінпанель будується індивідуально під завдання клієнта. '
            'Каталог товарів, форми заявок, замовлення, аналітика — лише те, '
            'що справді потрібне вашому бізнесу. Жодних зайвих розділів, '
            'які плутають та гальмують роботу.'
        ),
    },
    {
        'order': 2,
        'title': 'Унікальна на ринку України',
        'text': (
            'PrometeyLabs розробляє адмінпанелі, які відповідають реальним потребам '
            'українського бізнесу: мультимовність, інтеграція з платіжними системами, '
            'автоматичні сповіщення. Текст та зображення замінюються в кілька кліків '
            'через зручний інтерфейс без участі розробника.'
        ),
    },
]


class Command(BaseCommand):
    help = 'Seed feature blocks for /portfolio-beta/'

    def handle(self, *args, **options):
        if PortfolioFeatureBlock.objects.exists():
            self.stdout.write(self.style.WARNING(
                'Feature blocks already exist. Skipping. '
                'Use Django admin to edit them.'
            ))
            return

        for data in BLOCKS:
            payload = {
                **data,
                'title_ru': translate_ua_to_ru(data['title']),
                'text_ru': translate_ua_to_ru(data['text']),
            }
            PortfolioFeatureBlock.objects.create(**payload)
            self.stdout.write(self.style.SUCCESS(f'Created: {data["title"]}'))

        self.stdout.write(self.style.SUCCESS('Done: 3 feature blocks created.'))
