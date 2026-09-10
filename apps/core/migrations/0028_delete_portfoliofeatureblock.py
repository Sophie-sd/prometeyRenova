from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_portfolioproject_en_cs_i18n'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PortfolioFeatureBlock',
        ),
    ]
