# Migration to rename the Employee table from core_employee to auth_employee

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_employee'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL for PostgreSQL and SQLite
            sql='ALTER TABLE core_employee RENAME TO auth_employee;',
            reverse_sql='ALTER TABLE auth_employee RENAME TO core_employee;',
        ),
    ]
