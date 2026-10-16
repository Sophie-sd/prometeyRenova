"""Канон 16.10.2026: пожиттєва гарантія на код + 1 рік безкоштовної підтримки (усі КП)."""

import re

from django.db import migrations

SEED_UA = '<p>Ми надаємо <strong>пожиттєву гарантію на код</strong>: технічні баги, допущені з нашої вини, виправляємо безкоштовно без обмеження строку, а також <strong>1 рік безкоштовної підтримки</strong> з моменту запуску.</p>'
SEED_RU = '<p>Мы предоставляем <strong>пожизненную гарантию на код</strong>: технические баги, допущенные по нашей вине, исправляем бесплатно без ограничения срока, а также <strong>1 год бесплатной поддержки</strong> с момента запуска.</p>'
SEED_EN = '<p>We provide a <strong>lifetime code warranty</strong>: technical bugs caused by us are fixed free of charge with no time limit, plus <strong>1 year of free support</strong> from launch.</p>'

UA_RE = re.compile(r'<p>Ми надаємо <strong>(?:пожиттєву гарантію|1 рік гарант[^<]*)</strong>[^<]*?</p>')
RU_RE = re.compile(r'<p>Мы предоставляем <strong>(?:пожизненную гарантию|1 год гарант[^<]*)</strong>[^<]*?</p>')
EN_RE = re.compile(r'<p>We (?:provide|offer)[^<]*<strong>[^<]*(?:warranty|guarantee)[^<]*</strong>[^<]*?</p>', re.I)


def forwards(apps, schema_editor):
    Proposal = apps.get_model('core', 'Proposal')
    names = [f.name for f in Proposal._meta.fields if f.name.startswith('guarantee_html')]
    for p in Proposal.objects.all():
        fields = []
        for name in names:
            old = getattr(p, name) or ''
            val = UA_RE.sub(SEED_UA, old)
            val = RU_RE.sub(SEED_RU, val)
            val = EN_RE.sub(SEED_EN, val)
            if val != old:
                setattr(p, name, val)
                fields.append(name)
        if fields:
            p.save(update_fields=fields)

    Package = apps.get_model('core', 'ProposalPackage')
    pnames = [f.name for f in Package._meta.fields if f.get_internal_type() in ('TextField', 'CharField')]
    for pkg in Package.objects.all():
        fields = []
        for name in pnames:
            old = getattr(pkg, name) or ''
            val = old.replace('1 рік гарантії на код', 'пожиттєва гарантія на код і 1 рік безкоштовної підтримки')
            val = val.replace('1 год гарантии на код', 'пожизненная гарантия на код и 1 год бесплатной поддержки')
            if val != old:
                setattr(pkg, name, val)
                fields.append(name)
        if fields:
            pkg.save(update_fields=fields)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_portfolioproject_category'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
