import secrets

from django.db import migrations, models


def fill_console_keys(apps, schema_editor):
    DemoShop = apps.get_model('demoshop', 'DemoShop')
    used = set(
        DemoShop.objects.exclude(console_key__isnull=True).values_list('console_key', flat=True)
    )
    for shop in DemoShop.objects.filter(console_key__isnull=True).iterator():
        key = secrets.token_urlsafe(18)
        while key in used:
            key = secrets.token_urlsafe(18)
        used.add(key)
        shop.console_key = key
        shop.save(update_fields=['console_key'])


class Migration(migrations.Migration):

    dependencies = [
        ('demoshop', '0007_clear_shopcategory_icons'),
    ]

    operations = [
        migrations.AddField(
            model_name='demoshop',
            name='console_key',
            field=models.CharField(max_length=32, null=True, unique=True),
        ),
        migrations.RunPython(fill_console_keys, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='demoshop',
            name='console_key',
            field=models.CharField(
                editable=False, max_length=32, unique=True, verbose_name='Ключ кабінету',
            ),
        ),
    ]
