"""Додати DemoLandingClient право delete_landinglead (видалення заявок)."""
from django.db import migrations


def grant_delete_landinglead(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    group = Group.objects.filter(name='DemoLandingClient').first()
    if group is None:
        return
    try:
        perm = Permission.objects.get(
            content_type__app_label='demolanding',
            codename='delete_landinglead',
        )
    except Permission.DoesNotExist:
        return
    group.permissions.add(perm)


def revoke_delete_landinglead(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    group = Group.objects.filter(name='DemoLandingClient').first()
    if group is None:
        return
    try:
        perm = Permission.objects.get(
            content_type__app_label='demolanding',
            codename='delete_landinglead',
        )
    except Permission.DoesNotExist:
        return
    group.permissions.remove(perm)


class Migration(migrations.Migration):
    dependencies = [
        ('demolanding', '0002_demolandingclient_group'),
    ]

    operations = [
        migrations.RunPython(grant_delete_landinglead, revoke_delete_landinglead),
    ]
