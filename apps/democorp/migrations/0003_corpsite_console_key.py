import secrets

from django.db import migrations, models


def fill_console_keys(apps, schema_editor):
    CorpSite = apps.get_model('democorp', 'CorpSite')
    used = set(
        CorpSite.objects.exclude(console_key__isnull=True).values_list('console_key', flat=True)
    )
    for site in CorpSite.objects.filter(console_key__isnull=True).iterator():
        key = secrets.token_urlsafe(18)
        while key in used:
            key = secrets.token_urlsafe(18)
        used.add(key)
        site.console_key = key
        site.save(update_fields=['console_key'])


class Migration(migrations.Migration):

    dependencies = [
        ('democorp', '0002_democorpclient_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpsite',
            name='console_key',
            field=models.CharField(max_length=32, null=True, unique=True),
        ),
        migrations.RunPython(fill_console_keys, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='corpsite',
            name='console_key',
            field=models.CharField(
                editable=False, max_length=32, unique=True, verbose_name='Ключ кабінету',
            ),
        ),
    ]
