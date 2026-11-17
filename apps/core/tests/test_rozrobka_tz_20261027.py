"""Нові блоки /rozrobka-sajtiv/: порядок, портфоліо, FAQ, без другої ціни."""
from django.test import TestCase


def _landing(html):
    start = html.find('id="plRsRoot"')
    end = html.find('id="pl-rs-calc"')
    return html[start:end]


class RozrobkaTzBlocksTests(TestCase):
    def test_uk_order_cases_and_faq(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        root = _landing(html)
        compare = root.find('Замовити сайт у студії чи зробити в конструкторі')
        process = root.find('Як ми створюємо сайт')
        admin = root.find('Адмінка залишається у вас')
        work = root.find('Широке портфоліо сайтів на різну тематику')
        reviews = root.find('Відгуки клієнтів на Google')
        faq = root.find('Часті питання про розробку сайтів')
        self.assertTrue(0 < compare < process < admin < work < reviews < faq)
        self.assertNotIn('Проєкти в проді', root)
        self.assertNotIn('Усе портфоліо', root)
        self.assertEqual(root.count('data-pf-screen'), 7)
        self.assertIn('portfolio/screens/fpsu-desktop.webp', root)
        self.assertIn('portfolio/screens/ajeres-desktop.webp', root)
        self.assertIn('portfolio/screens/pokrivlya-desktop.webp', root)
        self.assertIn('portfolio/screens/elit-fasad-desktop.webp', root)
        self.assertIn('images/rozrobka/portfolio/varvarova.webp', root)
        self.assertIn('https://www.fpsu.org.ua/', root)
        self.assertIn('https://ajeres.uz/', root)
        self.assertIn('30 днів', root)
        self.assertIn('Детальніше про проєкт', root)
        self.assertIn('Задача', root)
        self.assertIn('Офіційний портал ФПУ', root)
        self.assertEqual(root.count('<details'), 11)
        self.assertIn('Чи зможу я сам змінювати сайт?', root)
        self.assertIn('Чому не зробити сайт у конструкторі?', root)
        self.assertNotIn('150', root)
        self.assertNotIn('пожиттєва', root.lower())
        self.assertNotIn('youtube', root)
        self.assertNotIn('<iframe', root)
        self.assertIn('data-pl-rs-video="giim7h-DlVg"', root)
        self.assertIn('data-pl-rs-video="UFPyLvLMp7M"', root)
        self.assertIn('Пн–Пт 10:00–18:00', html)
        self.assertIn('href="#pl-rs-calc"', root)
        self.assertNotIn('style=', root)
        self.assertEqual(html.count('<h1'), 1)

    def test_ru_keeps_current_page_without_new_blocks(self):
        html = self.client.get('/ru/rozrobka-sajtiv/').content.decode()
        root = _landing(html)
        self.assertNotIn('Широке портфоліо сайтів на різну тематику', root)
        self.assertNotIn('Відгуки клієнтів на Google', root)
        self.assertNotIn('data-pf-screen', root)
        self.assertNotIn('Пн–Пт 10:00–18:00', html)
        self.assertIn('href="/ru/portfolio/"', root)
        self.assertIn('data-modal="call-request-modal"', root)
        self.assertIn('href="/ru/calculator/"', root)

    def test_lead_and_prices_stay(self):
        html = self.client.get('/rozrobka-sajtiv/').content.decode()
        root = _landing(html)
        self.assertIn('data-modal="call-request-modal"', root)
        self.assertIn('href="/calculator/"', root)
        self.assertIn('tel:+380639520565', root)
        self.assertEqual(root.count('data-pl-rs-amount'), 6)
        self.assertNotIn('<form', root)
