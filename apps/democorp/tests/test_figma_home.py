"""Figma-редизайн demo-корп сайту: CMS-слоти рендеряться, вимкнений рейтинг ховає картку."""
from datetime import date

from django.test import Client, TestCase
from django.urls import reverse

from apps.core.proposal_models import Proposal
from apps.democorp.content_models import CorpBlock
from apps.democorp.services.provision import provision_demo_corp
from apps.democorp.templatetags.democorp_tags import accent


class FigmaHomeTests(TestCase):
    def setUp(self):
        proposal = Proposal.objects.create(
            slug='corp-figma-kp', client_name='Figma Client', title='KP',
            issued_on=date(2026, 10, 9), is_published=True,
            kind=Proposal.DemoKind.CORPORATE, corp_catalog=True,
        )
        self.site = provision_demo_corp(proposal)
        self.url = reverse('democorp:home', kwargs={'slug': self.site.slug})

    def test_home_renders_figma_sections(self):
        response = Client().get(self.url)
        self.assertEqual(response.status_code, 200)
        for marker in ('dc-hero', 'id="examples"', 'id="process"', 'id="reviews"', 'id="cta"',
                       'class="dc-accent"', 'dc-rating__value', 'democorp/css/demo.css'):
            self.assertContains(response, marker)
        self.assertNotContains(response, 'democorp/css/home.css')

    def test_cms_edit_changes_page_and_rating_toggle_hides_card(self):
        CorpBlock.objects.filter(tenant=self.site, page='production', key='step_label').update(value_text='Етап')
        CorpBlock.objects.filter(tenant=self.site, page='home', key='rating_visible').update(value_text='0')
        response = Client().get(self.url)
        self.assertContains(response, 'Етап 1')
        self.assertNotContains(response, 'dc-rating__value')

    def test_accent_filter_escapes(self):
        self.assertEqual(str(accent('<b> люди', 'люди')), '&lt;b&gt; <span class="dc-accent">люди</span>')
        self.assertEqual(str(accent('текст', 'нема')), 'текст')
