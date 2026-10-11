# Generated manually 2026-10-12 00:15
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demoshop', '0008_demoshop_console_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='demoshop',
            name='quote_mode',
            field=models.BooleanField(
                default=False,
                help_text='Приховує ціни та кошик, показує "Poptat cenu" замість "До кошика"',
                verbose_name='Режим запиту ціни (B2B)',
            ),
        ),
    ]
