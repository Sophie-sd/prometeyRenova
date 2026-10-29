import apps.core.proposal_models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_proposalimport'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProposalHeroImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=apps.core.proposal_models.proposal_hero_image_upload_to, verbose_name='Фото')),
                ('original_name', models.CharField(blank=True, default='', max_length=255, verbose_name='Оригінальна назва файлу')),
                ('alt_uk', models.CharField(blank=True, default='', max_length=200, verbose_name='Alt (UK)')),
                ('alt_ru', models.CharField(blank=True, default='', max_length=200, verbose_name='Alt (RU)')),
                ('alt_en', models.CharField(blank=True, default='', max_length=200, verbose_name='Alt (EN)')),
                ('alt_cs', models.CharField(blank=True, default='', max_length=200, verbose_name='Alt (CS)')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активне')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Оновлено')),
                ('proposal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hero_images', to='core.proposal', verbose_name='КП')),
            ],
            options={
                'verbose_name': 'Hero-фото КП',
                'verbose_name_plural': 'Hero-фото КП',
                'ordering': ('proposal', 'order', 'id'),
                'constraints': [models.UniqueConstraint(fields=('proposal', 'order'), name='uniq_proposal_hero_order')],
            },
        ),
    ]
