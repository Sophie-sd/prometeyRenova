"""Група DemoLandingClient: доступ клієнта лише до власного лендінгу (RunPython, оборотна)."""
from django.db import migrations

DEMO_LANDING_CLIENT_PERMS = [
    ('demolanding', 'view_landingoffer'), ('demolanding', 'add_landingoffer'),
    ('demolanding', 'change_landingoffer'), ('demolanding', 'delete_landingoffer'),
    ('demolanding', 'view_landinggalleryimage'), ('demolanding', 'add_landinggalleryimage'),
    ('demolanding', 'change_landinggalleryimage'), ('demolanding', 'delete_landinggalleryimage'),
    ('demolanding', 'view_landingbeforeafter'), ('demolanding', 'add_landingbeforeafter'),
    ('demolanding', 'change_landingbeforeafter'), ('demolanding', 'delete_landingbeforeafter'),
    ('demolanding', 'view_landingtestimonial'), ('demolanding', 'add_landingtestimonial'),
    ('demolanding', 'change_landingtestimonial'), ('demolanding', 'delete_landingtestimonial'),
    ('demolanding', 'view_landingpartner'), ('demolanding', 'add_landingpartner'),
    ('demolanding', 'change_landingpartner'), ('demolanding', 'delete_landingpartner'),
    ('demolanding', 'view_landinglead'), ('demolanding', 'change_landinglead'),
    ('demolanding', 'view_landingblock'), ('demolanding', 'change_landingblock'),
]


def create_demo_landing_client_group(apps, schema_editor):
    from django.apps import apps as global_apps
    from django.contrib.auth.management import create_permissions

    # Permission-рядки для щойно створених моделей з'являються лише через
    # post_migrate (після завершення всього `migrate`-запуску), тобто ПІСЛЯ
    # цього RunPython, якщо 0001+0002 застосовують в одній команді. Явний
    # виклик тут гарантує, що Permission.objects.get() нижче їх знайде.
    # `apps.get_app_config()` (історичний registry миграції) не має
    # `models_module` — потрібен справжній `django.apps.apps`.
    create_permissions(global_apps.get_app_config('demolanding'), verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    group, _created = Group.objects.get_or_create(name='DemoLandingClient')
    perm_objs = []
    for app_label, codename in DEMO_LANDING_CLIENT_PERMS:
        try:
            perm_objs.append(Permission.objects.get(content_type__app_label=app_label, codename=codename))
        except Permission.DoesNotExist:
            continue
    group.permissions.set(perm_objs)


def remove_demo_landing_client_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='DemoLandingClient').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('demolanding', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_demo_landing_client_group, remove_demo_landing_client_group),
    ]
