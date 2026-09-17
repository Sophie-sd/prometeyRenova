"""Група DemoClient: доступ клієнта лише до власного демо-магазину (RunPython, оборотна)."""
from django.db import migrations

DEMO_CLIENT_PERMS = [
    ('demoshop', 'view_shopcategory'), ('demoshop', 'add_shopcategory'), ('demoshop', 'change_shopcategory'),
    ('demoshop', 'view_shopproduct'), ('demoshop', 'add_shopproduct'), ('demoshop', 'change_shopproduct'),
    ('demoshop', 'view_shopproductimage'), ('demoshop', 'add_shopproductimage'),
    ('demoshop', 'change_shopproductimage'), ('demoshop', 'delete_shopproductimage'),
    ('demoshop', 'view_shopreview'), ('demoshop', 'add_shopreview'), ('demoshop', 'change_shopreview'),
    ('demoshop', 'view_shoporder'), ('demoshop', 'change_shoporder'),
    ('demoshop', 'view_shoporderitem'),
    ('demoshop', 'view_shopblock'), ('demoshop', 'change_shopblock'),
    ('demoshop', 'view_shopheroslide'), ('demoshop', 'add_shopheroslide'),
    ('demoshop', 'change_shopheroslide'), ('demoshop', 'delete_shopheroslide'),
]


def create_demo_client_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    group, _created = Group.objects.get_or_create(name='DemoClient')
    perm_objs = []
    for app_label, codename in DEMO_CLIENT_PERMS:
        try:
            perm_objs.append(Permission.objects.get(content_type__app_label=app_label, codename=codename))
        except Permission.DoesNotExist:
            continue
    group.permissions.set(perm_objs)


def remove_demo_client_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='DemoClient').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('demoshop', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_demo_client_group, remove_demo_client_group),
    ]
