# Generated manually for Proposal CMS models

from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_update_contact_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(help_text='URL: /proposal/<slug>/ — робіть невгадуваним', max_length=160, unique=True, verbose_name='Slug')),
                ('client_name', models.CharField(max_length=200, verbose_name='Клієнт')),
                ('title', models.CharField(max_length=300, verbose_name='Заголовок')),
                ('title_ru', models.CharField(blank=True, max_length=300, verbose_name='Заголовок (RU)')),
                ('lead', models.TextField(blank=True, verbose_name='Лід / підзаголовок')),
                ('lead_ru', models.TextField(blank=True, verbose_name='Лід (RU)')),
                ('issued_on', models.DateField(verbose_name='Дата пропозиції')),
                ('intro_html', models.TextField(blank=True, verbose_name='Про компанію / стек (HTML)')),
                ('intro_html_ru', models.TextField(blank=True, verbose_name='Про компанію / стек (HTML) (RU)')),
                ('guarantee_html', models.TextField(blank=True, verbose_name='Гарантія (HTML)')),
                ('guarantee_html_ru', models.TextField(blank=True, verbose_name='Гарантія (HTML) (RU)')),
                ('cta_label', models.CharField(default='Обговорити проєкт', max_length=120, verbose_name='Текст CTA')),
                ('cta_label_ru', models.CharField(blank=True, max_length=120, verbose_name='Текст CTA (RU)')),
                ('is_published', models.BooleanField(db_index=True, default=False, verbose_name='Опубліковано')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Оновлено')),
            ],
            options={
                'verbose_name': 'Комерційна пропозиція',
                'verbose_name_plural': 'Комерційні пропозиції',
                'ordering': ('order', '-issued_on'),
            },
        ),
        migrations.CreateModel(
            name='ProposalModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(default=1, verbose_name='Номер')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('title_ru', models.CharField(blank=True, max_length=200, verbose_name='Заголовок (RU)')),
                ('description', models.TextField(blank=True, verbose_name='Опис')),
                ('description_ru', models.TextField(blank=True, verbose_name='Опис (RU)')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('proposal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='core.proposal', verbose_name='Пропозиція')),
            ],
            options={
                'verbose_name': 'Модуль',
                'verbose_name_plural': 'Модулі',
                'ordering': ('order', 'number', 'id'),
            },
        ),
        migrations.CreateModel(
            name='ProposalPackage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Назва пакету')),
                ('name_ru', models.CharField(blank=True, max_length=200, verbose_name='Назва пакету (RU)')),
                ('scope', models.TextField(blank=True, verbose_name='Що входить')),
                ('scope_ru', models.TextField(blank=True, verbose_name='Що входить (RU)')),
                ('duration', models.CharField(blank=True, max_length=100, verbose_name='Термін')),
                ('duration_ru', models.CharField(blank=True, max_length=100, verbose_name='Термін (RU)')),
                ('price', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Вартість')),
                ('currency', models.CharField(default='€', max_length=8, verbose_name='Валюта')),
                ('is_recommended', models.BooleanField(default=False, verbose_name='Рекомендований')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('proposal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='core.proposal', verbose_name='Пропозиція')),
            ],
            options={
                'verbose_name': 'Пакет',
                'verbose_name_plural': 'Пакети',
                'ordering': ('order', 'id'),
            },
        ),
        migrations.CreateModel(
            name='ProposalSpec',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('spec', 'ТЗ / деталі проєкту'), ('payment', 'Умови оплати')], db_index=True, default='spec', max_length=20, verbose_name='Тип')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('title_ru', models.CharField(blank=True, max_length=200, verbose_name='Заголовок (RU)')),
                ('body', models.TextField(blank=True, verbose_name='Текст')),
                ('body_ru', models.TextField(blank=True, verbose_name='Текст (RU)')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('proposal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specs', to='core.proposal', verbose_name='Пропозиція')),
            ],
            options={
                'verbose_name': 'Специфікація',
                'verbose_name_plural': 'Специфікації',
                'ordering': ('kind', 'order', 'id'),
            },
        ),
    ]
