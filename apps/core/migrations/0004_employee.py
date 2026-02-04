# Generated migration for Employee model with app_label='auth'

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_add_email_sent_tracking'),
        ('auth', '0012_alter_user_first_name_max_length'),  # Dependency on auth app
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(max_length=100, verbose_name="Прізвище")),
                ('first_name', models.CharField(max_length=100, verbose_name="Ім'я")),
                ('patronymic', models.CharField(blank=True, max_length=100, verbose_name='По батькові')),
                ('position', models.CharField(max_length=200, verbose_name='Посада')),
                ('hire_date', models.DateField(blank=True, null=True, verbose_name='Дата прийому на роботу')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон')),
                ('bio', models.TextField(blank=True, verbose_name='Короткий опис / Біо')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Активний')),
                ('order', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Порядок відображення')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Оновлено')),
            ],
            options={
                'verbose_name': 'Співробітник',
                'verbose_name_plural': 'Співробітники',
                'ordering': ['order', 'last_name', 'first_name'],
            },
        ),
        migrations.AddIndex(
            model_name='employee',
            index=models.Index(fields=['order', 'is_active'], name='core_employee_order_is_act_idx'),
        ),
        migrations.AddIndex(
            model_name='employee',
            index=models.Index(fields=['is_active'], name='core_employee_is_active_idx'),
        ),
    ]
