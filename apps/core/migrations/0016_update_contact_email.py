from django.db import migrations, models

OLD_EMAIL = 'prometeylabs@gmail.com'
NEW_EMAIL = 'info@prometeylabs.com'


def update_contact_email(apps, schema_editor):
    SiteContactSettings = apps.get_model('core', 'SiteContactSettings')
    SiteContactSettings.objects.filter(email=OLD_EMAIL).update(email=NEW_EMAIL)


def revert_contact_email(apps, schema_editor):
    SiteContactSettings = apps.get_model('core', 'SiteContactSettings')
    SiteContactSettings.objects.filter(email=NEW_EMAIL).update(email=OLD_EMAIL)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_add_ru_content_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitecontactsettings',
            name='email',
            field=models.EmailField(default=NEW_EMAIL, max_length=254, verbose_name='Email'),
        ),
        migrations.RunPython(update_contact_email, revert_contact_email),
    ]
