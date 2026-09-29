from decimal import Decimal

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_ecom_base_price_1000'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeRateSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uah_per_eur', models.DecimalField(
                    decimal_places=4,
                    default=Decimal('0'),
                    help_text='Нуль ховає кнопку гривні на сайті.',
                    max_digits=12,
                    validators=[django.core.validators.MinValueValidator(Decimal('0'))],
                    verbose_name='Гривень за 1 €',
                )),
                ('usd_per_eur', models.DecimalField(
                    decimal_places=4,
                    default=Decimal('0'),
                    help_text='Нуль ховає кнопку долара на сайті.',
                    max_digits=12,
                    validators=[django.core.validators.MinValueValidator(Decimal('0'))],
                    verbose_name='Доларів за 1 €',
                )),
                ('czk_per_eur', models.DecimalField(
                    decimal_places=4,
                    default=Decimal('0'),
                    help_text='Нуль ховає кнопку крони на сайті.',
                    max_digits=12,
                    validators=[django.core.validators.MinValueValidator(Decimal('0'))],
                    verbose_name='Крон за 1 €',
                )),
            ],
            options={
                'verbose_name': 'Курс валют',
                'verbose_name_plural': 'Курс валют',
            },
        ),
    ]
