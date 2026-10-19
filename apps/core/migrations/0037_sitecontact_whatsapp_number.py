from django.db import migrations

NEW_WHATSAPP_URL = 'https://wa.me/380995891477'
# Старий дефолт, що генерувався з телефону відображення (не чіпаємо сам телефон).
OLD_FALLBACK_URL = 'https://wa.me/380639520565'


def set_whatsapp_url(apps, schema_editor):
    """Кнопка WhatsApp веде на окремий номер (+380995891477).

    Телефон на сайті лишається +380639520565. Оновлюємо лише порожнє поле або
    старе fallback-значення, щоб не затерти кастомне посилання, якщо його вже
    виставили в адмінці.
    """
    SiteContactSettings = apps.get_model('core', 'SiteContactSettings')
    obj = SiteContactSettings.objects.filter(pk=1).first() or SiteContactSettings.objects.first()
    if obj is None:
        return
    if not obj.whatsapp_url or obj.whatsapp_url.strip() in ('', OLD_FALLBACK_URL):
        obj.whatsapp_url = NEW_WHATSAPP_URL
        obj.save(update_fields=['whatsapp_url'])


def unset_whatsapp_url(apps, schema_editor):
    SiteContactSettings = apps.get_model('core', 'SiteContactSettings')
    obj = SiteContactSettings.objects.filter(pk=1).first() or SiteContactSettings.objects.first()
    if obj is None:
        return
    if obj.whatsapp_url.strip() == NEW_WHATSAPP_URL:
        obj.whatsapp_url = ''
        obj.save(update_fields=['whatsapp_url'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_proposal_guarantee_lifetime_support'),
    ]

    operations = [
        migrations.RunPython(set_whatsapp_url, unset_whatsapp_url),
    ]
