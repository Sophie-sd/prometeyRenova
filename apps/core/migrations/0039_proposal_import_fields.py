from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_client_site_url_logo_static'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proposal',
            options={'ordering': ('order', '-issued_on'),
                     'permissions': [('can_import_proposal', "Може імпортувати, м'яко видаляти та відновлювати КП")],
                     'verbose_name': 'Комерційна пропозиція', 'verbose_name_plural': 'Комерційні пропозиції'},
        ),
        migrations.AddField(
            model_name='proposal', name='source',
            field=models.CharField(choices=[('seed', 'Seed (код)'), ('import', 'Імпорт (адмінка)')],
                                   db_index=True, default='seed', max_length=10, verbose_name='Джерело'),
        ),
        migrations.AddField(
            model_name='proposal', name='deleted_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Видалено (soft)'),
        ),
        migrations.AddField(
            model_name='proposal', name='deleted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='deleted_proposals', to=settings.AUTH_USER_MODEL, verbose_name='Ким видалено'),
        ),
        migrations.AddField(
            model_name='proposal', name='pair_slug',
            field=models.SlugField(blank=True, db_index=True, max_length=200, null=True, verbose_name='Slug парного КП'),
        ),
        migrations.AddConstraint(
            model_name='proposal',
            constraint=models.UniqueConstraint(condition=models.Q(deleted_at__isnull=True, pair_slug__isnull=False),
                                               fields=('pair_slug',), name='uniq_proposal_pair_slug_alive'),
        ),
    ]
