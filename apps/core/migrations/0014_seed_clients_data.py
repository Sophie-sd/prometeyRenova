from django.db import migrations


def seed_clients_forward(apps, schema_editor):
    # No-op: seed_clients uses the current Client model (fields from later migrations),
    # so it cannot run at this point of a fresh migrate. build.sh / scripts/start.sh run it.
    return


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_client'),
    ]

    operations = [
        migrations.RunPython(seed_clients_forward, migrations.RunPython.noop),
    ]
