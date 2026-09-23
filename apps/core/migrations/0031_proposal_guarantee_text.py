"""Один текст «Надійність та гарантія» на всіх КП."""

from django.db import migrations

GUARANTEE_HTML = (
    '<p>Ми впевнені в якості нашої інженерної бази. Оскільки сайт створюється '
    'на чистому коді без нестабільних сторонніх плагінів, він не потребує '
    'постійних ризикованих оновлень, які ламають верстку.</p>'
    '<p>Ми надаємо <strong>пожиттєву гарантію</strong> на працездатність '
    'нашого коду протягом усього періоду життя ресурсу.</p>'
)

GUARANTEE_HTML_RU = (
    '<p>Мы уверены в качестве нашей инженерной базы. Поскольку сайт создаётся '
    'на чистом коде без нестабильных сторонних плагинов, он не нуждается '
    'в постоянных рискованных обновлениях, которые ломают вёрстку.</p>'
    '<p>Мы предоставляем <strong>пожизненную гарантию</strong> на работоспособность '
    'нашего кода в течение всего периода жизни ресурса.</p>'
)


def set_guarantee(apps, schema_editor):
    Proposal = apps.get_model('core', 'Proposal')
    Proposal.objects.update(
        guarantee_html=GUARANTEE_HTML,
        guarantee_html_ru=GUARANTEE_HTML_RU,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_formsubmission_telegram_bot'),
    ]

    operations = [
        migrations.RunPython(set_guarantee, migrations.RunPython.noop),
    ]
