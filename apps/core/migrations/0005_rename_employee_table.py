# Migration to rename the Employee table from core_employee to auth_employee

from django.db import connection, migrations


def rename_employee_table(apps, schema_editor):
    names = set(connection.introspection.table_names())
    if 'core_employee' in names and 'auth_employee' not in names:
        qn = connection.ops.quote_name
        with connection.cursor() as cursor:
            cursor.execute(
                f'ALTER TABLE {qn("core_employee")} RENAME TO {qn("auth_employee")}'
            )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_employee'),
    ]

    operations = [
        migrations.RunPython(rename_employee_table, migrations.RunPython.noop),
    ]
