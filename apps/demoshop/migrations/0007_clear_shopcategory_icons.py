"""Прибрати emoji-іконки з назв категорій демо-магазину."""

from django.db import migrations


def clear_category_icons(apps, schema_editor):
    ShopCategory = apps.get_model('demoshop', 'ShopCategory')
    ShopCategory.objects.exclude(icon='').update(icon='')


class Migration(migrations.Migration):

    dependencies = [
        ('demoshop', '0006_shopblock_value_text_cs_shopcategory_name_cs_and_more'),
    ]

    operations = [
        migrations.RunPython(clear_category_icons, migrations.RunPython.noop),
    ]
