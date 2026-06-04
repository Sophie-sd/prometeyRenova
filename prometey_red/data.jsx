// Shared data + tokens for all variants — pulled from real template strings.

const PROMETEY_DATA = {
  whyTitle: "Чому варто обрати PrometeyLabs",
  whyIntro:
    "Ми розробляємо сайти, якими справді легко керувати. Жодних обмежень шаблонних рішень — тільки чистий, оптимізований код та індивідуальна архітектура. Завдяки детальній розробці адмін-частини, ви можете самостійно оновлювати весь контент сайту в кілька кліків. Ми створюємо фундамент, готовий до інтеграцій та росту разом із вашим бізнесом.",

  whyCards: [
    {
      icon: "assets/icons/calendar.svg",
      titleAccent: "Прозорі строки,",
      titleRest: "яких ми дотримуємося",
      subtitle: "Базові терміни виконання:",
      list: [
        ["Лендінги:", "3–7 днів"],
        ["Корпоративні сайти:", "7–14 днів"],
        ["Інтернет-магазини:", "14–21 днів"],
        ["Веб-додатки / SaaS:", "14–30 днів"],
      ],
      note:
        "Точний час розробки залежить від складності дизайну, інтеграцій та функціоналу — визначаємо на консультації.",
    },
    {
      icon: "assets/icons/dollar.svg",
      titleAccent: "Справедлива вартість",
      titleRest: "та гнучкі умови оплати",
      subtitle: "Середні діапазони цін:",
      list: [
        ["Лендінги:", "$150–350"],
        ["Корпоративні сайти:", "$350–500"],
        ["E-commerce:", "$500–800"],
        ["Веб-додатки:", "$700–1000+"],
      ],
      note:
        "Пропонуємо розбиття оплати на етапи — без переплат та прихованих умов.",
    },
    {
      icon: "assets/icons/shield.svg",
      titleAccent: "5-річна гарантія",
      titleRest: "на наші продукти",
      subtitle: "Гарантія включає:",
      list: [
        ["", "Виправлення технічних помилок"],
        ["", "Підтримку працездатності коду"],
        ["", "Реакцію на критичні технічні збої"],
        ["", "Відповідність функціоналу ТЗ"],
      ],
      note:
        "Не включає: нові функції, оновлення дизайну, інтеграції з новими сервісами.",
    },
    {
      icon: "assets/icons/ai.svg",
      titleAccent: "Впровадження ШІ",
      titleRest: "у ваші бізнес-задачі",
      subtitle: "Що отримуєте:",
      list: [
        ["", "Автоматизація рутини на сайті"],
        ["", "ШІ-консультант для клієнтів"],
        ["", "Інтеграція з вашими процесами"],
        ["", "Оптимізація витрат на support"],
      ],
      note:
        "Результат: повна автоматизація взаємодії з клієнтами та новий рівень цифрового сервісу.",
    },
  ],

  whyFooter:
    "Спеціалісти PrometeyLabs мають роки практики у веб-розробці, дизайні, інтеграціях, мобільних додатках та інтернет-маркетингу. Це гарантує, що ваш проєкт буде реалізований системно, технологічно та з розумінням бізнес-задач.",

  servicesTitle: "Послуги PrometeyLabs",
  services: [
    {
      n: "01",
      bg: "assets/services/web.png",
      bgMobile: "assets/services/web_mob.png",
      title: "Web-розробка",
      desc: "Сайти під ключ, лендінги, інтернет-магазини, веб-додатки, телеграм-боти",
    },
    {
      n: "02",
      bg: "assets/services/mob.png",
      bgMobile: "assets/services/mob_mob.png",
      title: "Мобільні застосунки",
      desc: "iOS та Android додатки з сучасним дизайном",
    },
    {
      n: "03",
      bg: "assets/services/media.png",
      bgMobile: "assets/services/media_mob.png",
      title: "Реклама та соц. мережі",
      desc: "Google Ads, Meta Ads, TikTok Ads, SMM, контент",
    },
    {
      n: "04",
      bg: "assets/services/edu.png",
      bgMobile: "assets/services/edu_mob.png",
      title: "Навчання",
      desc: "Програмування та AI від нуля до працевлаштування",
    },
  ],

  clientsTitle: "Наші клієнти",
  clients: [
    { img: "assets/portfolio/adiabatic.png", name: "Adiabatic" },
    { img: "assets/portfolio/airinua.png", name: "Air in UA" },
    { img: "assets/portfolio/beautyshop.png", name: "Beauty Shop" },
    { img: "assets/portfolio/coresync.png", name: "CoreSync" },
    { img: "assets/portfolio/playvision.png", name: "PlayVision" },
    { img: "assets/portfolio/polygraph.png", name: "Polygraph" },
    { img: "assets/portfolio/pulvas_store.png", name: "Pulvas Store" },
    { img: "assets/portfolio/redrabbit.png", name: "Red Rabbit" },
    { img: "assets/portfolio/speakup.png", name: "SpeakUp" },
  ],

  ctaTitle: "Готові почати?",
  ctaText:
    "Зв'яжіться з нами для безкоштовної консультації та розрахунку вартості проєкту",
  ctaPrimary: "Розрахувати вартість",
  ctaSecondary: "Telegram-консультація",
};

window.PROMETEY_DATA = PROMETEY_DATA;
