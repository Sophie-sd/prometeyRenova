from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0008_alter_paymentlink_exchange_rate_usd_to_uah'),
    ]

    operations = [
        migrations.RenameField(
            model_name='PaymentLink',
            old_name='amount_usd',
            new_name='amount',
        ),
        migrations.RenameField(
            model_name='PaymentLink',
            old_name='exchange_rate_usd_to_uah',
            new_name='exchange_rate',
        ),
        migrations.AddField(
            model_name='paymentlink',
            name='currency',
            field=models.CharField(
                choices=[('USD', 'USD ($)'), ('EUR', 'EUR (€)'), ('UAH', 'UAH (₴)')],
                default='USD',
                max_length=3,
                verbose_name='Валюта',
            ),
        ),
        migrations.AlterField(
            model_name='paymentlink',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Сума'),
        ),
        migrations.AlterField(
            model_name='paymentlink',
            name='exchange_rate',
            field=models.DecimalField(
                decimal_places=2,
                default='40.00',
                help_text='Ігнорується при валюті UAH',
                max_digits=12,
                verbose_name='Курс до UAH',
            ),
        ),
    ]
