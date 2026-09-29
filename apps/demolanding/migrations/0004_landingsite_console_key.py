import secrets

from django.db import migrations, models


def fill_console_keys(apps, schema_editor):
    LandingSite = apps.get_model('demolanding', 'LandingSite')
    used = set(
        LandingSite.objects.exclude(console_key__isnull=True).values_list('console_key', flat=True)
    )
    for site in LandingSite.objects.filter(console_key__isnull=True).iterator():
        key = secrets.token_urlsafe(18)
        while key in used:
            key = secrets.token_urlsafe(18)
        used.add(key)
        site.console_key = key
        site.save(update_fields=['console_key'])


class Migration(migrations.Migration):

    dependencies = [
        ('demolanding', '0003_grant_delete_landinglead'),
    ]

    operations = [
        migrations.AddField(
            model_name='landingsite',
            name='console_key',
            field=models.CharField(max_length=32, null=True, unique=True),
        ),
        migrations.RunPython(fill_console_keys, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='landingsite',
            name='console_key',
            field=models.CharField(
                editable=False, max_length=32, unique=True, verbose_name='Ключ кабінету',
            ),
        ),
    ]
