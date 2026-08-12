from django.db import migrations, models


def seed_site_contact_settings(apps, schema_editor):
    SiteContactSettings = apps.get_model('core', 'SiteContactSettings')
    if not SiteContactSettings.objects.filter(pk=1).exists():
        SiteContactSettings.objects.create(
            pk=1,
            phone_display='+38 (063) 952-05-65',
            phone_e164='380639520565',
            email='info@prometeylabs.com',
            instagram_url='https://instagram.com/prometeylabs',
            facebook_url='https://facebook.com/prometeylabs',
            linkedin_url='https://linkedin.com/company/prometeylabs',
            telegram_url='https://t.me/prometeylabs',
            maps_zoom=15,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_add_gclid_utm_keycrm_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteContactSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_display', models.CharField(default='+38 (063) 952-05-65', max_length=32, verbose_name='Телефон (відображення)')),
                ('phone_e164', models.CharField(default='380639520565', help_text='Без +, наприклад 380639520565', max_length=20, verbose_name='Телефон (цифри для посилань)')),
                ('email', models.EmailField(default='info@prometeylabs.com', max_length=254, verbose_name='Email')),
                ('instagram_url', models.URLField(default='https://instagram.com/prometeylabs', verbose_name='Instagram')),
                ('facebook_url', models.URLField(default='https://facebook.com/prometeylabs', verbose_name='Facebook')),
                ('linkedin_url', models.URLField(default='https://linkedin.com/company/prometeylabs', verbose_name='LinkedIn')),
                ('telegram_url', models.URLField(default='https://t.me/prometeylabs', verbose_name='Telegram')),
                ('whatsapp_url', models.URLField(blank=True, help_text='Якщо порожньо — генерується з телефону', verbose_name='WhatsApp (опційно)')),
                ('viber_url', models.URLField(blank=True, help_text='Якщо порожньо — генерується з телефону', verbose_name='Viber (опційно)')),
                ('maps_latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Широта (Google Maps)')),
                ('maps_longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Довгота (Google Maps)')),
                ('maps_zoom', models.PositiveSmallIntegerField(default=15, verbose_name='Масштаб карти')),
                ('google_maps_embed_url', models.URLField(blank=True, help_text='Повний src з Google Maps «Поділитися → Вбудувати». Має пріоритет над координатами.', max_length=500, verbose_name='URL вбудованої карти (iframe src)')),
            ],
            options={
                'verbose_name': 'Контакти та карта',
                'verbose_name_plural': 'Контакти та карта',
            },
        ),
        migrations.RunPython(seed_site_contact_settings, migrations.RunPython.noop),
    ]
