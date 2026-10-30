"""Copy-handoff 5908f41 для КП corp-budivnytstvo-g1by (UA+RU). Ідемпотентно.

За замовчуванням dry-run; запис лише з --apply. На проді — тільки після «так» Олега
(видаляє дубль-картку «Гарантія» серед recommendation).
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.proposal_models import Proposal, ProposalSpec
from apps.core.proposal_visual_models import ProposalHighlight

SLUG = 'corp-budivnytstvo-g1by'
RECS = [
    ('Окремі шляхи для бізнесу й приватних замовників',
     "Два чіткі входи на головній: для забудовників і компаній — генпідряд і комерційні об'єкти, для приватних клієнтів — котеджі й ремонт. Кожен бачить свої послуги й одразу потрапляє до потрібної форми.",
     'Отдельные пути для бизнеса и частных заказчиков',
     'Два понятных входа на главной: для застройщиков и компаний — генподряд и коммерческие объекты, для частных клиентов — коттеджи и ремонт. Каждый видит свои услуги и сразу попадает в нужную форму.'),
    ('Етапи роботи від заявки до здачі',
     "Сторінка «Як ми працюємо»: консультація, кошторис, договір, будівництво, здача об'єкта. Замовник заздалегідь розуміє процес і менше сумнівається перед дзвінком.",
     'Этапы работы от заявки до сдачи',
     'Страница «Как мы работаем»: консультация, смета, договор, строительство, сдача объекта. Заказчик заранее понимает процесс и меньше сомневается перед звонком.'),
    ('Дзвінок і месенджер в один дотик',
     "Закріплені на смартфоні кнопки дзвінка, Telegram і Viber, щоб замовник міг зв'язатися прямо з об'єкта чи з дороги, не шукаючи контакти.",
     'Звонок и мессенджер в одно касание',
     'Закреплённые на смартфоне кнопки звонка, Telegram и Viber, чтобы заказчик мог связаться прямо с объекта или с дороги, не ища контакты.'),
    ('Географія робіт',
     'Блок або сторінка з містами й регіонами, де компанія будує. Це допомагає в локальному пошуку Google і відсіює заявки, які ви не берете.',
     'География работ',
     'Блок или страница с городами и регионами, где компания строит. Это помогает в локальном поиске Google и отсеивает заявки, которые вы не берёте.'),
]
LEAD_FROM, LEAD_TO = 'Кодописний', 'Написаний з нуля'
HL = [('title', 'Enterprise-безпека', 'Корпоративна безпека'),
      ('title_ru', 'Enterprise-безопасность', 'Корпоративная безопасность')]


class Command(BaseCommand):
    help = 'Застосувати Copy 5908f41 до КП corp-budivnytstvo-g1by (dry-run без --apply)'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true')

    def handle(self, *args, apply, **opts):
        p = Proposal.objects.filter(slug=SLUG).first()
        if not p:
            raise CommandError(f'КП {SLUG} не знайдено в цій БД')
        plan = []
        recs = list(p.specs.filter(kind=ProposalSpec.Kind.RECOMMENDATION).order_by('order', 'pk'))
        keep_titles = {r[0] for r in RECS}
        for r in recs:
            if r.title not in keep_titles:
                plan.append(f'DELETE recommendation #{r.pk} «{r.title}»')
        for i, (t, b, tr, br) in enumerate(RECS):
            plan.append(f'UPSERT recommendation {i}: «{t}»')
        if LEAD_FROM in (p.lead or ''):
            plan.append(f'lead: «{LEAD_FROM}» → «{LEAD_TO}»')
        for h in p.highlights.all():
            for f, a, b in HL:
                if a in (getattr(h, f) or ''):
                    plan.append(f'highlight #{h.pk}.{f}: «{a}» → «{b}»')
        for line in plan:
            self.stdout.write(line)
        if not apply:
            self.stdout.write('Dry-run. Додайте --apply.')
            return
        with transaction.atomic():
            for r in recs:
                if r.title not in keep_titles:
                    r.delete()
            for i, (t, b, tr, br) in enumerate(RECS):
                obj = p.specs.filter(kind=ProposalSpec.Kind.RECOMMENDATION, title=t).first() or \
                    ProposalSpec(proposal=p, kind=ProposalSpec.Kind.RECOMMENDATION, title=t)
                obj.order, obj.body, obj.title_ru, obj.body_ru = i, b, tr, br
                obj.save()
            if LEAD_FROM in (p.lead or ''):
                p.lead = p.lead.replace(LEAD_FROM, LEAD_TO)
                p.save(update_fields=['lead', 'updated_at'])
            for h in p.highlights.all():
                changed = []
                for f, a, b in HL:
                    v = getattr(h, f) or ''
                    if a in v:
                        setattr(h, f, v.replace(a, b)); changed.append(f)
                if changed:
                    h.save(update_fields=changed)
        self.stdout.write(self.style.SUCCESS('Застосовано.'))
