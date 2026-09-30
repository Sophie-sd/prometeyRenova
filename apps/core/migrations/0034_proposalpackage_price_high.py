from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_exchangeratesettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposalpackage',
            name='price_high',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Якщо заповнено, на картці помаранчевим іде діапазон від вартості до цієї суми.',
                max_digits=12,
                null=True,
                verbose_name='Вартість до',
            ),
        ),
    ]
