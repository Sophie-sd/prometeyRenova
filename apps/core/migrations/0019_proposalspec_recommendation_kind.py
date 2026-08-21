# Generated manually for ProposalSpec.Kind.RECOMMENDATION

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_proposal_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposalspec',
            name='kind',
            field=models.CharField(
                choices=[
                    ('spec', 'ТЗ / деталі проєкту'),
                    ('payment', 'Умови оплати'),
                    ('recommendation', 'Рекомендації PrometeyLabs'),
                ],
                db_index=True,
                default='spec',
                max_length=20,
                verbose_name='Тип',
            ),
        ),
    ]
