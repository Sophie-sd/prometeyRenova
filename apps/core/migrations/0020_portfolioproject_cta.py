from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_merge_20260720_invoices'),
        ('core', '0019_proposalspec_recommendation_kind'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolioproject',
            name='cta_label',
            field=models.CharField(
                blank=True,
                help_text='Якщо порожньо — «Більше інформації»',
                max_length=120,
                verbose_name='Текст кнопки',
            ),
        ),
        migrations.AddField(
            model_name='portfolioproject',
            name='cta_label_ru',
            field=models.CharField(
                blank=True,
                max_length=120,
                verbose_name='Текст кнопки (RU)',
            ),
        ),
        migrations.AddField(
            model_name='portfolioproject',
            name='cta_url',
            field=models.CharField(
                blank=True,
                help_text='Внутрішнє (/contacts/) або повне https://…. Без URL кнопка не показується.',
                max_length=500,
                verbose_name='Посилання кнопки',
            ),
        ),
        migrations.AlterField(
            model_name='portfolioproject',
            name='order',
            field=models.PositiveIntegerField(
                default=0,
                help_text=(
                    'Сортування у видачі. Шахматка (фото ліворуч/праворуч) '
                    'і колір фону (помаранчевий → сірий → фіолетовий) рахуються '
                    'автоматично з позиції в списку.'
                ),
                verbose_name='Порядок на /portfolio/',
            ),
        ),
    ]
