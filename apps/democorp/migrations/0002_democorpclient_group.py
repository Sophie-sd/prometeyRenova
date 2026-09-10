"""Група DemoCorpClient: доступ клієнта лише до власного сайту (RunPython, оборотна)."""
from django.db import migrations

DEMO_CORP_CLIENT_PERMS = [
    ('democorp', 'view_corpproductionstep'), ('democorp', 'add_corpproductionstep'),
    ('democorp', 'change_corpproductionstep'), ('democorp', 'delete_corpproductionstep'),
    ('democorp', 'view_corpgalleryimage'), ('democorp', 'add_corpgalleryimage'),
    ('democorp', 'change_corpgalleryimage'), ('democorp', 'delete_corpgalleryimage'),
    ('democorp', 'view_corptestimonial'), ('democorp', 'add_corptestimonial'),
    ('democorp', 'change_corptestimonial'), ('democorp', 'delete_corptestimonial'),
    ('democorp', 'view_corppartner'), ('democorp', 'add_corppartner'),
    ('democorp', 'change_corppartner'), ('democorp', 'delete_corppartner'),
    ('democorp', 'view_corplead'), ('democorp', 'change_corplead'),
    ('democorp', 'view_corpblock'), ('democorp', 'change_corpblock'),
    ('democorp', 'view_corpcategory'), ('democorp', 'add_corpcategory'),
    ('democorp', 'change_corpcategory'), ('democorp', 'delete_corpcategory'),
    ('democorp', 'view_corpproduct'), ('democorp', 'add_corpproduct'),
    ('democorp', 'change_corpproduct'), ('democorp', 'delete_corpproduct'),
    ('democorp', 'view_corpproductimage'), ('democorp', 'add_corpproductimage'),
    ('democorp', 'change_corpproductimage'), ('democorp', 'delete_corpproductimage'),
]


def create_demo_corp_client_group(apps, schema_editor):
    from django.apps import apps as global_apps
    from django.contrib.auth.management import create_permissions

    # Permission-рядки для щойно створених моделей з'являються лише через
    # post_migrate (після завершення всього `migrate`-запуску), тобто ПІСЛЯ
    # цього RunPython, якщо 0001+0002 застосовують в одній команді. Явний
    # виклик тут гарантує, що Permission.objects.get() нижче їх знайде.
    # `apps.get_app_config()` (історичний registry миграції) не має
    # `models_module` — потрібен справжній `django.apps.apps`.
    create_permissions(global_apps.get_app_config('democorp'), verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    group, _created = Group.objects.get_or_create(name='DemoCorpClient')
    perm_objs = []
    for app_label, codename in DEMO_CORP_CLIENT_PERMS:
        try:
            perm_objs.append(Permission.objects.get(content_type__app_label=app_label, codename=codename))
        except Permission.DoesNotExist:
            continue
    group.permissions.set(perm_objs)


def remove_demo_corp_client_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='DemoCorpClient').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('democorp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_demo_corp_client_group, remove_demo_corp_client_group),
    ]
