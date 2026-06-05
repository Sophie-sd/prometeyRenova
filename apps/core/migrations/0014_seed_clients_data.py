from django.core.management import call_command
from django.db import migrations


def seed_clients_forward(apps, schema_editor):
    call_command('seed_clients')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_client'),
    ]

    operations = [
        migrations.RunPython(seed_clients_forward, migrations.RunPython.noop),
    ]
