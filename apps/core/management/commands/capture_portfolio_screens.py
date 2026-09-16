"""
Знімки головних сторінок сайтів-проєктів для картки /portfolio/.

Запускається ЛОКАЛЬНО (не на Render): потребує Playwright + Chromium.

    python3 -m pip install playwright
    python3 -m playwright install chromium
    python3 manage.py capture_portfolio_screens

Результат — WebP у static/images/portfolio/screens/<slug>-desktop.webp
і <slug>-mobile.webp + JSON з title/description/h1 у /tmp/portfolio_meta.json
(використовується для написання текстів картки).
"""
import json
from pathlib import Path

from urllib.parse import urljoin

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.core.portfolio_seed_data import PORTFOLIO_PROJECTS

DESKTOP_VIEWPORT = {'width': 1440, 'height': 900}
MOBILE_VIEWPORT = {'width': 390, 'height': 844}
DESKTOP_CAP_HEIGHT = 6000
MOBILE_CAP_HEIGHT = 3500
MOBILE_UA = (
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) '
    'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'
)
DESKTOP_UA = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
)
COOKIE_HIDE_SELECTORS = (
    '[class*="cookie" i]',
    '[id*="cookie" i]',
    '[class*="consent" i]',
    '[id*="consent" i]',
)
META_OUT = Path('/tmp/portfolio_meta.json')


class Command(BaseCommand):
    help = 'Знімає full-page WebP головних сторінок сайтів портфоліо (Playwright, локально)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            action='append',
            dest='slugs',
            help='Обмежити знімок конкретним(и) slug (можна кілька разів)',
        )
        parser.add_argument(
            '--only-missing',
            action='store_true',
            help='Пропустити slug, для яких обидва WebP вже існують',
        )
        parser.add_argument(
            '--out',
            default='static/images/portfolio/screens',
            help='Каталог для WebP (відносно кореня проєкту)',
        )
        parser.add_argument(
            '--headed',
            action='store_true',
            help='Показати вікно браузера (для проходження Cloudflare challenge вручну)',
        )

    def handle(self, *args, **options):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise CommandError(
                'Playwright не встановлено. Виконайте:\n'
                '  python3 -m pip install playwright pillow\n'
                '  python3 -m playwright install chromium'
            ) from exc

        try:
            from PIL import Image
        except ImportError as exc:
            raise CommandError('Pillow не встановлено: python3 -m pip install pillow') from exc

        out_dir = Path(settings.BASE_DIR) / options['out']
        out_dir.mkdir(parents=True, exist_ok=True)

        wanted_slugs = set(options['slugs'] or [])
        only_missing = options['only_missing']
        headed = options['headed']

        items = [p for p in PORTFOLIO_PROJECTS if p.get('site_url')]
        if wanted_slugs:
            items = [p for p in items if p['slug'] in wanted_slugs]

        if not items:
            self.stdout.write(self.style.WARNING('Немає проєктів із site_url для знімку.'))
            return

        meta_report = {}
        ok, skipped, failed = 0, 0, 0

        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=not headed,
                args=['--disable-blink-features=AutomationControlled'],
            )
            try:
                for item in items:
                    slug = item['slug']
                    url = item['site_url']
                    locale = item.get('capture_locale', 'uk-UA')
                    desktop_path = out_dir / f'{slug}-desktop.webp'
                    mobile_path = out_dir / f'{slug}-mobile.webp'

                    if only_missing and desktop_path.is_file() and mobile_path.is_file():
                        self.stdout.write(f'⏭  {slug}: вже є, пропущено')
                        skipped += 1
                        continue

                    self.stdout.write(f'📸 {slug} — {url}')
                    try:
                        meta = self._capture_one(
                            browser, url, locale, desktop_path, mobile_path, Image,
                            extra_paths=item.get('capture_paths') or [],
                            white_bg=(slug == 'auto-lot'),
                        )
                        meta_report[slug] = meta
                        ok += 1
                    except Exception as exc:  # noqa: BLE001 — best-effort по кожному сайту окремо
                        self.stdout.write(self.style.ERROR(f'✖ {slug}: {exc}'))
                        failed += 1
                        continue
            finally:
                browser.close()

        if meta_report:
            existing = {}
            if META_OUT.is_file():
                try:
                    existing = json.loads(META_OUT.read_text(encoding='utf-8'))
                except (ValueError, OSError):
                    existing = {}
            existing.update(meta_report)
            META_OUT.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding='utf-8')
            self.stdout.write(f'📝 Meta записано у {META_OUT}')

        self.stdout.write(
            self.style.SUCCESS(f'Готово: {ok} знято, {skipped} пропущено, {failed} з помилкою.')
        )

    def _capture_one(
        self, browser, url, locale, desktop_path, mobile_path, Image,
        extra_paths=None, white_bg=False,
    ):
        urls = [url]
        for path in extra_paths or []:
            joined = urljoin(url, path)
            if joined not in urls:
                urls.append(joined)

        meta = {}
        desktop_pngs = []
        mobile_pngs = []
        for index, page_url in enumerate(urls):
            png, page_meta = self._shoot(
                browser, page_url, locale, DESKTOP_VIEWPORT, DESKTOP_UA, 1,
                collect_meta=(index == 0),
                white_bg=white_bg,
            )
            desktop_pngs.append(png)
            if index == 0:
                meta = page_meta
            png, _unused = self._shoot(
                browser, page_url, locale, MOBILE_VIEWPORT, MOBILE_UA, 2,
                collect_meta=False,
                white_bg=white_bg,
            )
            mobile_pngs.append(png)

        self._save_capped_webp(
            desktop_pngs, desktop_path, DESKTOP_CAP_HEIGHT, Image, white_bg=white_bg,
        )
        self._save_capped_webp(
            mobile_pngs, mobile_path, MOBILE_CAP_HEIGHT, Image, white_bg=white_bg,
        )
        return meta or {}

    def _shoot(self, browser, url, locale, viewport, ua, dsf, collect_meta, white_bg=False):
        context = browser.new_context(
            viewport=viewport,
            device_scale_factor=dsf,
            user_agent=ua,
            locale=locale,
            ignore_https_errors=True,
        )
        page = context.new_page()
        page_meta = {}
        try:
            try:
                page.goto(url, wait_until='networkidle', timeout=45000)
            except Exception:  # noqa: BLE001 — fallback на повільні/аналітичні сайти
                page.goto(url, wait_until='load', timeout=45000)
                page.wait_for_timeout(2500)

            if collect_meta:
                page_meta = {
                    'title': page.title(),
                    'description': page.eval_on_selector(
                        'meta[name="description"]', 'el => el.content',
                    ) if page.query_selector('meta[name="description"]') else '',
                    'h1': (page.eval_on_selector('h1', 'el => el.innerText') or '').strip()
                    if page.query_selector('h1') else '',
                    'lang': page.eval_on_selector('html', 'el => el.lang') or '',
                }

            # Тригер lazy/reveal: повільніший скрол, щоб картинки встигли.
            page.evaluate(
                """
                async () => {
                  const step = 400;
                  const delay = (ms) => new Promise((r) => setTimeout(r, ms));
                  let last = -1;
                  for (let i = 0; i < 120; i += 1) {
                    window.scrollBy(0, step);
                    await delay(550);
                    const h = Math.max(
                      document.body.scrollHeight,
                      document.documentElement.scrollHeight,
                    );
                    const atBottom = window.scrollY + window.innerHeight >= h - 4;
                    if (h === last && atBottom) break;
                    last = h;
                  }
                  await delay(2500);
                  for (let i = 0; i < 120; i += 1) {
                    if (window.scrollY <= 0) break;
                    window.scrollBy(0, -step);
                    await delay(550);
                  }
                  window.scrollTo(0, 0);
                }
                """
            )

            try:
                page.wait_for_function(
                    '() => Array.from(document.images).every((img) => img.complete)',
                    timeout=15000,
                )
            except Exception:  # noqa: BLE001 — best-effort
                pass

            try:
                page.wait_for_load_state('networkidle', timeout=12000)
            except Exception:  # noqa: BLE001 — аналітика/long-poll не блокує знімок
                pass

            try:
                page.evaluate(
                    """
                    () => {
                      document.querySelectorAll('video').forEach((video) => {
                        video.muted = true;
                        try {
                          if (video.readyState >= 2 && video.duration) {
                            video.currentTime = Math.min(0.4, video.duration);
                          }
                        } catch (_err) {}
                        const play = video.play();
                        if (play && typeof play.catch === 'function') {
                          play.catch(() => {});
                        }
                      });
                    }
                    """
                )
                page.wait_for_timeout(800)
                page.evaluate(
                    "() => document.querySelectorAll('video').forEach((video) => video.pause())"
                )
            except Exception:  # noqa: BLE001 — не всі сайти мають video
                pass

            try:
                page.evaluate(
                    """
                    () => {
                      const ytId = (src) => {
                        const match = String(src || '').match(
                          /(?:youtube(?:-nocookie)?\\.com\\/embed\\/|youtu\\.be\\/)([A-Za-z0-9_-]{6,})/
                        );
                        return match ? match[1] : '';
                      };
                      document.querySelectorAll('iframe').forEach((iframe) => {
                        const id = ytId(iframe.src || iframe.getAttribute('data-src'));
                        if (!id) return;
                        const img = document.createElement('img');
                        img.src = 'https://i.ytimg.com/vi/' + id + '/hqdefault.jpg';
                        img.alt = '';
                        img.style.width = '100%';
                        img.style.height = '100%';
                        img.style.objectFit = 'cover';
                        img.style.display = 'block';
                        iframe.replaceWith(img);
                      });
                    }
                    """
                )
                page.wait_for_function(
                    '() => Array.from(document.images).every((img) => img.complete)',
                    timeout=15000,
                )
            except Exception:  # noqa: BLE001 — YouTube poster не критичний
                pass

            for selector in COOKIE_HIDE_SELECTORS:
                try:
                    page.eval_on_selector_all(
                        selector,
                        "els => els.forEach(el => { el.style.setProperty('display', 'none', 'important'); })",
                    )
                except Exception:  # noqa: BLE001 — best-effort, не критично
                    pass

            if white_bg:
                page.evaluate(
                    """
                    () => {
                      const root = document.documentElement;
                      const body = document.body;
                      root.style.setProperty('background', '#ffffff', 'important');
                      if (body) {
                        body.style.setProperty('background', '#ffffff', 'important');
                        body.style.setProperty('background-color', '#ffffff', 'important');
                      }
                    }
                    """
                )

            page.wait_for_timeout(5000)
            png_bytes = page.screenshot(full_page=True, type='png', timeout=60000)
        finally:
            context.close()

        return png_bytes, page_meta

    @staticmethod
    def _save_capped_webp(png_list, out_path, cap_height, Image, white_bg=False):
        import io

        if isinstance(png_list, (bytes, bytearray)):
            png_list = [png_list]

        frames = []
        for png_bytes in png_list:
            with Image.open(io.BytesIO(png_bytes)) as im:
                frames.append(im.convert('RGB'))

        width = max(frame.width for frame in frames)
        total_h = 0
        resized = []
        for frame in frames:
            if frame.width != width:
                height = max(1, round(frame.height * width / frame.width))
                frame = frame.resize((width, height))
            resized.append(frame)
            total_h += frame.height

        canvas_h = min(total_h, cap_height)
        fill = (255, 255, 255) if white_bg else (0, 0, 0)
        canvas = Image.new('RGB', (width, canvas_h), fill)
        y = 0
        for frame in resized:
            if y >= canvas_h:
                break
            crop_h = min(frame.height, canvas_h - y)
            canvas.paste(frame.crop((0, 0, frame.width, crop_h)), (0, y))
            y += crop_h
        canvas.save(out_path, format='WEBP', quality=82, method=6)
