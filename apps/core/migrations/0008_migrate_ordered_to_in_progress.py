# Generated manually on 2026-02-04
# Migration to convert any existing 'ordered' status records to 'in_progress'

from django.db import migrations


def migrate_ordered_to_in_progress(apps, schema_editor):
    """Convert all 'ordered' status records to 'in_progress'"""
    FormSubmission = apps.get_model('core', 'FormSubmission')
    FormSubmission.objects.filter(status='ordered').update(status='in_progress')


def reverse_migration(apps, schema_editor):
    """Reverse migration - convert back if needed (unlikely to be used)"""
    # Note: We won't convert back since 'ordered' is being removed
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_update_form_submission_statuses'),
    ]

    operations = [
        migrations.RunPython(migrate_ordered_to_in_progress, reverse_migration),
    ]
