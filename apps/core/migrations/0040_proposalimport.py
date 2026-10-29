from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_proposal_import_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProposalImport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('upload', 'Завантаження'), ('rollback', 'Відкат')], default='upload', max_length=10, verbose_name='Тип')),
                ('version', models.PositiveIntegerField(default=1, verbose_name='Версія')),
                ('file', models.FileField(blank=True, upload_to='proposal_imports/%Y/%m/', verbose_name='Файл імпорту (zip)')),
                ('original_name', models.CharField(blank=True, default='', max_length=255, verbose_name='Оригінальна назва файлу')),
                ('sha256', models.CharField(blank=True, max_length=64, null=True, unique=True, verbose_name='SHA-256 zip')),
                ('manifest', models.JSONField(blank=True, null=True, verbose_name='manifest.json')),
                ('status', models.CharField(choices=[('pending', 'Очікує'), ('processing', 'Обробка'), ('success', 'Успіх'), ('error', 'Помилка')], default='pending', max_length=12, verbose_name='Статус')),
                ('log', models.JSONField(blank=True, default=list, verbose_name='Лог')),
                ('error', models.TextField(blank=True, default='', verbose_name='Помилка')),
                ('snapshot_before', models.JSONField(blank=True, null=True, verbose_name='Знімок КП до імпорту (JSON)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Оновлено')),
                ('finished_at', models.DateTimeField(blank=True, null=True, verbose_name='Завершено')),
                ('proposal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='imports', to='core.proposal', verbose_name='КП')),
                ('rollback_of', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='rollbacks', to='core.proposalimport', verbose_name='Відкат імпорту')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proposal_imports', to=settings.AUTH_USER_MODEL, verbose_name='Хто імпортував')),
            ],
            options={
                'verbose_name': 'Імпорт КП',
                'verbose_name_plural': 'Імпорти КП',
                'ordering': ('-created_at',),
                'indexes': [models.Index(fields=['status', 'created_at'], name='core_pimp_status_created_idx'),
                            models.Index(fields=['proposal', '-version'], name='core_pimp_proposal_ver_idx')],
                'constraints': [models.UniqueConstraint(condition=models.Q(proposal__isnull=False), fields=('proposal', 'version'), name='uniq_proposalimport_proposal_version'),
                                models.CheckConstraint(condition=models.Q(('kind', 'upload'), ('rollback_of__isnull', False), _connector='OR'), name='ck_proposalimport_rollback_has_target'),
                                models.CheckConstraint(condition=models.Q(('kind', 'rollback'), ('sha256__isnull', False), _connector='OR'), name='ck_proposalimport_upload_has_sha256')],
            },
        ),
    ]
