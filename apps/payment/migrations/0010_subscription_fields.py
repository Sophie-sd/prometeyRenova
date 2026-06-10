from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0009_multi_currency'),
    ]

    operations = [
        # ── Нові поля підписки на PaymentLink ──────────────────────────────
        migrations.AddField(
            model_name='paymentlink',
            name='is_subscription',
            field=models.BooleanField(
                default=False,
                verbose_name='Активувати підписку',
                help_text='Якщо увімкнено — перший платіж збереже картку клієнта для щомісячного списання.',
            ),
        ),
        migrations.AddField(
            model_name='paymentlink',
            name='subscription_status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('pending_card', "Очікує прив'язки картки"),
                    ('active', 'Активна'),
                    ('paused', 'Призупинена'),
                    ('cancelled', 'Скасована'),
                ],
                default='',
                max_length=20,
                verbose_name='Статус підписки',
            ),
        ),
        migrations.AddField(
            model_name='paymentlink',
            name='card_token',
            field=models.CharField(
                blank=True,
                default='',
                max_length=255,
                verbose_name='Токен картки',
            ),
        ),
        migrations.AddField(
            model_name='paymentlink',
            name='next_charge_date',
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name='Наступне списання',
            ),
        ),
        migrations.AddField(
            model_name='paymentlink',
            name='last_charged_at',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='Останнє списання',
            ),
        ),
        # ── Нова таблиця SubscriptionCharge ────────────────────────────────
        migrations.CreateModel(
            name='SubscriptionCharge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_payment', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='subscription_charges',
                    to='payment.paymentlink',
                    verbose_name='Підписка',
                )),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Виконується'),
                        ('success', 'Успішно'),
                        ('failed', 'Помилка'),
                    ],
                    default='pending',
                    max_length=20,
                    verbose_name='Статус',
                )),
                ('amount_uah', models.DecimalField(
                    decimal_places=2,
                    max_digits=14,
                    verbose_name='Сума UAH',
                )),
                ('monobank_invoice_id', models.CharField(
                    blank=True,
                    default='',
                    max_length=128,
                    verbose_name='Invoice ID Monobank',
                )),
                ('error_message', models.TextField(
                    blank=True,
                    default='',
                    verbose_name='Помилка',
                )),
                ('charged_at', models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name='Дата списання',
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Списання по підписці',
                'verbose_name_plural': 'Списання по підписках',
                'ordering': ['-created_at'],
            },
        ),
    ]
