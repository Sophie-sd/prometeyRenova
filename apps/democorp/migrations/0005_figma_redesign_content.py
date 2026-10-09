"""Figma-редизайн demo-корп сайту (2026-10): оновлює лише НЕзмінені клієнтом дефолти.

- блоки, чиє значення дорівнює старому дефолту, → новий дефолт (тексти клієнта не чіпаємо);
- видаляє мертві ключі реєстру (cta.point_1..3, production.step_1..4 — не рендерились / прибрані з дизайну);
- hero-фото з seed (hero.webp) → hero-glow.webp (фон hero з Figma);
- аватари seed-відгуків, якщо порожні;
- legacy-кольори «dark luxury» → палітра Figma.
"""
from django.db import migrations

BLOCK_UPDATES = {
    ('home', 'hero_title'): (
        {'': 'Кілька сторінок — і люди пишуть вам', 'en': 'A few pages — and people write to you',
         'cs': 'Pár stránek — a lidé vám napíšou', 'ru': 'Несколько страниц — и люди пишут вам'},
        {'': 'Кілька сторінок —\nі люди пишуть вам', 'en': 'A few pages —\nand people write to you',
         'cs': 'Pár stránek —\na lidé vám napíšou', 'ru': 'Несколько страниц —\nи люди пишут вам'},
    ),
    ('home', 'catalog_teaser_title'): (
        {'': 'Приклади сайтів, які можна замовити', 'en': 'Example sites you can order',
         'cs': 'Příklady webů, které si můžete objednat', 'ru': 'Примеры сайтов, которые можно заказать'},
        {'': 'Приклади\nсайтів, які можна замовити', 'en': 'Examples\nof sites you can order',
         'cs': 'Příklady\nwebů, které si můžete objednat', 'ru': 'Примеры\nсайтов, которые можно заказать'},
    ),
    ('home', 'stat_windows_label'): (
        {'': 'сторінок у комплекті', 'en': 'pages in the set', 'cs': 'stránek v sadě', 'ru': 'страниц в комплекте'},
        {'': 'В комплекті', 'en': 'In the set', 'cs': 'V sadě', 'ru': 'В комплекте'},
    ),
    ('home', 'stat_years_label'): (
        {'': 'днів до старту', 'en': 'days to launch', 'cs': 'dní do startu', 'ru': 'дней до старта'},
        {'': 'До старту', 'en': 'To launch', 'cs': 'Do startu', 'ru': 'До старта'},
    ),
    ('home', 'stat_warranty_label'): (
        {'': 'зручно з телефону', 'en': 'easy on the phone', 'cs': 'pohodlné v telefonu', 'ru': 'удобно с телефона'},
        {'': 'Зручно з телефону', 'en': 'Easy on the phone', 'cs': 'Pohodlné v telefonu', 'ru': 'Удобно с телефона'},
    ),
    ('home', 'stat_dealers_label'): (
        {'': 'мови одразу', 'en': 'languages from day one', 'cs': 'jazyky hned', 'ru': 'языка сразу'},
        {'': 'Одразу', 'en': 'From day one', 'cs': 'Hned', 'ru': 'Сразу'},
    ),
    ('production', 'title'): (
        {'': 'Як ми робимо корпоративний сайт', 'en': 'How we make a corporate site',
         'cs': 'Jak děláme firemní web', 'ru': 'Как мы делаем корпоративный сайт'},
        {'': 'Як ми робимо корпоративний сайт?', 'en': 'How do we make a corporate site?',
         'cs': 'Jak děláme firemní web?', 'ru': 'Как мы делаем корпоративный сайт?'},
    ),
    ('cta', 'note'): (
        {'': 'Відповімо протягом робочого дня', 'en': 'We reply within a business day',
         'cs': 'Odpovíme během pracovního dne', 'ru': 'Ответим в течение рабочего дня'},
        {'': 'Відповідь протягом робочого дня', 'en': 'Reply within one business day',
         'cs': 'Odpověď během pracovního dne', 'ru': 'Ответ в течение рабочего дня'},
    ),
}

DEAD_KEYS = [('cta', 'point_1'), ('cta', 'point_2'), ('cta', 'point_3'),
             ('production', 'step_1'), ('production', 'step_2'),
             ('production', 'step_3'), ('production', 'step_4')]

AVATARS = {'Олена К.': 1, 'Ігор М.': 2, 'Марина Т.': 3, 'Дмитро В.': 4, 'Софія Л.': 5}

NEW_COLORS = {
    'color_primary': '#0D0D0D', 'color_primary_hover': '#141414', 'color_accent': '#D05300',
    'color_surface': '#0D0D0D', 'color_text': '#FFFFFF',
}
OLD_COLORS = {'#100D0C', '#181412', '#C99A44', '#FCF2EE'}


def _field(lang):
    return 'value_text' if not lang else f'value_text_{lang}'


def forwards(apps, schema_editor):
    CorpBlock = apps.get_model('democorp', 'CorpBlock')
    CorpSite = apps.get_model('democorp', 'CorpSite')
    CorpTestimonial = apps.get_model('democorp', 'CorpTestimonial')

    for (page, key), (old, new) in BLOCK_UPDATES.items():
        for block in CorpBlock.objects.filter(page=page, key=key):
            changed = []
            for lang, old_value in old.items():
                name = _field(lang)
                if (getattr(block, name) or '').strip() == old_value:
                    setattr(block, name, new[lang])
                    changed.append(name)
            if changed:
                block.save(update_fields=changed)

    for page, key in DEAD_KEYS:
        CorpBlock.objects.filter(page=page, key=key).delete()

    for site in CorpSite.objects.all():
        fields = []
        hero = site.hero_image.name or ''
        if not hero or hero.rsplit('/', 1)[-1].startswith('hero'):
            if 'hero-glow' not in hero:
                site.hero_image.name = 'democorp/hero/hero-glow.webp'
                fields.append('hero_image')
        for name, value in NEW_COLORS.items():
            current = (getattr(site, name) or '').upper()
            if not current or current in OLD_COLORS:
                setattr(site, name, value)
                fields.append(name)
        if fields:
            site.save(update_fields=fields)

    for item in CorpTestimonial.objects.filter(author_name__in=AVATARS.keys()):
        if not item.avatar:
            item.avatar.name = f'democorp/avatars/avatar-{AVATARS[item.author_name]}.webp'
            item.save(update_fields=['avatar'])


class Migration(migrations.Migration):
    dependencies = [
        ('democorp', '0004_figma_redesign'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
