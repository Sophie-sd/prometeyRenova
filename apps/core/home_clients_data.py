"""Клієнти для стрічки «Наші клієнти» (seed_clients).

Лише сайти, які є в портфоліо (portfolio_seed_projects_*) і живі: кожен
``site_url`` — фінальна адреса після ``curl -L`` (200, реальний контент),
перевірено 27.10.2026. Лого — з хедера сайту клієнта, підготовлене як квадратний
WebP 256/128 (лого по центру з відступом під коло) у
``static/images/clients/<slug>.webp`` і ``<slug>-128.webp``.

Порядок — від найвпізнаваніших. Ключ для ідемпотентності — ``name``.
"""

HOME_CLIENTS = [
    {'name': 'ФПУ', 'slug': 'fpsu', 'site_url': 'https://www.fpsu.org.ua/'},
    {'name': 'Play Vision', 'slug': 'playvision', 'site_url': 'https://playvision.com.ua/'},
    {'name': 'TEN clinic', 'slug': 'tenclinic', 'site_url': 'https://tenclinic.com.ua/'},
    {'name': 'OFION', 'slug': 'ofion', 'site_url': 'https://ofion.com.ua/'},
    {'name': 'Magnum', 'slug': 'magnum', 'site_url': 'https://magnum-tpc.com/uk/'},
    {'name': 'ZNOMax', 'slug': 'znomax', 'site_url': 'https://znomax.online/'},
    {'name': 'UCVN', 'slug': 'ucvn', 'site_url': 'https://ucvn.com.ua/'},
    {'name': 'Світ ПК', 'slug': 'svitpc', 'site_url': 'https://svitpc.com.ua/'},
    {'name': 'Boltiko', 'slug': 'boltiko', 'site_url': 'https://boltiko.com.ua/'},
    {'name': 'Domoteh', 'slug': 'domoteh', 'site_url': 'https://domoteh.shop/'},
    {'name': 'ЗубRoom', 'slug': 'zubroom', 'site_url': 'https://zubroom.com.ua/'},
    {'name': 'Air in UA', 'slug': 'airinua', 'site_url': 'https://www.airinua.com/'},
    {'name': 'GORDI market', 'slug': 'gordimarket', 'site_url': 'https://gordimarket.com.ua/'},
    {'name': 'Kylymy', 'slug': 'kylymy', 'site_url': 'https://carpet-haus.com.ua/'},
    {'name': 'Oyra', 'slug': 'oyra', 'site_url': 'https://oyra.com.ua/'},
    {'name': 'AJERES', 'slug': 'ajeres', 'site_url': 'https://ajeres.uz/en/'},
    {'name': 'Re-Charge', 'slug': 'recharge', 'site_url': 'https://recharge4gym.com.ua/uk/'},
    {'name': 'Фортуна Прінт', 'slug': 'fortprint', 'site_url': 'https://www.fortprint.com.ua/'},
    {'name': 'Soliron', 'slug': 'soliron', 'site_url': 'https://soliron.com.ua/'},
    {'name': 'Benzovoz', 'slug': 'benzovoz', 'site_url': 'https://www.benzovoz.com.ua/'},
    {'name': 'Football Generation', 'slug': 'footballgeneration', 'site_url': 'https://footballgeneration.com.ua/'},
    {'name': 'Метріум', 'slug': 'metrium', 'site_url': 'https://metrium.com.ua/'},
    {'name': 'Фенікс', 'slug': 'phoenixvet', 'site_url': 'https://www.phoenixvet.com.ua/'},
    {'name': 'Led Leader', 'slug': 'led-leader', 'site_url': 'https://led-leader.com.ua/'},
    {'name': 'Zelin', 'slug': 'zelin', 'site_url': 'https://zelin.com.ua/'},
    {'name': 'Європобут С', 'slug': 'evropobuts', 'site_url': 'https://evropobuts.com.ua/'},
    {'name': 'Geer', 'slug': 'geer', 'site_url': 'https://450geer.com.ua/'},
    {'name': 'DropRoom', 'slug': 'droproom', 'site_url': 'https://droproom.com.ua/'},
    {'name': 'Beauty Cake', 'slug': 'beautycake', 'site_url': 'https://beautycake.com.ua/'},
    {'name': 'Queen Drive', 'slug': 'queendrive', 'site_url': 'https://queendrive.com.ua/'},
    {'name': 'DISTAGEavto', 'slug': 'distageavto', 'site_url': 'https://www.distageavto.com/uk/'},
    {'name': 'Покрівля', 'slug': 'pokrivlya', 'site_url': 'https://pokrivlya.com.ua/'},
    {'name': 'Уманьтрансбуд', 'slug': 'vezhi-rozhnovskogo', 'site_url': 'https://vezhi-rozhnovskogo.com.ua/'},
]

for _order, _item in enumerate(HOME_CLIENTS):
    _item['order'] = _order
    _item['logo_static'] = f"images/clients/{_item['slug']}.webp"
