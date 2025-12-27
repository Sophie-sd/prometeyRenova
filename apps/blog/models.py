from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class BlogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Заголовок"))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_("URL"))
    excerpt = models.TextField(max_length=300, verbose_name=_("Короткий опис"))
    content = models.TextField(verbose_name=_("Контент"))
    seo_title = models.CharField(max_length=70, verbose_name=_("SEO заголовок"))
    seo_description = models.CharField(max_length=160, verbose_name=_("SEO опис"))
    keywords = models.CharField(max_length=255, verbose_name=_("Ключові слова"))
    
    # Нові поля для SEO
    meta_title = models.CharField(max_length=60, verbose_name=_("Meta Title"), blank=True)
    meta_description = models.CharField(max_length=160, verbose_name=_("Meta Description"), blank=True)
    og_title = models.CharField(max_length=60, verbose_name=_("OG Title"), blank=True)
    og_description = models.CharField(max_length=160, verbose_name=_("OG Description"), blank=True)
    
    # Додаткові поля
    reading_time = models.PositiveIntegerField(default=5, verbose_name=_("Час читання (хв)"))
    featured_image = models.ImageField(upload_to='blog/', verbose_name=_("Головне зображення"), blank=True)
    category = models.CharField(max_length=50, choices=[
        ('web-development', _('Веб-розробка')),
        ('courses', _('Курси програмування')),
        ('telegram-bots', _('Telegram боти')),
        ('business', _('Бізнес')),
        ('technology', _('Технології')),
        ('ai-development', _('AI розробка')),
        ('ai-agents', _('AI агенти')),
        ('ai-automation', _('AI автоматизація')),
    ], default='web-development', verbose_name=_("Категорія"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Створено"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Оновлено"))
    is_published = models.BooleanField(default=True, verbose_name=_("Опубліковано"))
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Стаття блогу")
        verbose_name_plural = _("Статті блогу")
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Автоматично заповнюємо meta поля якщо вони порожні
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.meta_description:
            self.meta_description = self.excerpt[:160]
        if not self.og_title:
            self.og_title = self.title[:60]
        if not self.og_description:
            self.og_description = self.excerpt[:160]
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:blog_detail', kwargs={'slug': self.slug})
    
    def get_keywords_list(self):
        """Повертає список ключових слів"""
        if self.keywords:
            return [keyword.strip() for keyword in self.keywords.split(',')]
        return []
    
    def get_reading_time_text(self):
        """Повертає текст часу читання"""
        if self.reading_time == 1:
            return "1 хвилина"
        elif self.reading_time < 5:
            return f"{self.reading_time} хвилини"
        else:
            return f"{self.reading_time} хвилин"
    
    def get_clean_content(self):
        """Повертає контент без зірочок та форматований для журнального стилю"""
        import re
        content = self.content
        
        # Прибираємо подвійні зірочки (жирний текст в markdown)
        content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)
        
        # Прибираємо одинарні зірочки
        content = content.replace('*', '')
        
        # Конвертуємо markdown заголовки в HTML
        content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        
        # Конвертуємо параграфи
        lines = content.split('\n')
        formatted_lines = []
        in_paragraph = False
        in_blockquote = False
        in_list = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                if in_paragraph:
                    formatted_lines.append('</p>')
                    in_paragraph = False
                if in_blockquote:
                    formatted_lines.append('</blockquote>')
                    in_blockquote = False
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                formatted_lines.append('')
            elif line.startswith('<h') or line.startswith('</h'):
                if in_paragraph:
                    formatted_lines.append('</p>')
                    in_paragraph = False
                if in_blockquote:
                    formatted_lines.append('</blockquote>')
                    in_blockquote = False
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                formatted_lines.append(line)
            elif line.startswith('>'):
                # Цитата (blockquote)
                if in_paragraph:
                    formatted_lines.append('</p>')
                    in_paragraph = False
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                if not in_blockquote:
                    formatted_lines.append('<blockquote>')
                    in_blockquote = True
                quote_text = line[1:].strip()
                if quote_text:
                    formatted_lines.append(f'<p>{quote_text}</p>')
            elif line.startswith('-'):
                if in_paragraph:
                    formatted_lines.append('</p>')
                    in_paragraph = False
                if in_blockquote:
                    formatted_lines.append('</blockquote>')
                    in_blockquote = False
                if not in_list:
                    formatted_lines.append('<ul>')
                    in_list = True
                formatted_lines.append(f'<li>{line[1:].strip()}</li>')
            else:
                if in_blockquote:
                    formatted_lines.append('</blockquote>')
                    in_blockquote = False
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                if not in_paragraph and not line.startswith('<'):
                    formatted_lines.append('<p>')
                    in_paragraph = True
                formatted_lines.append(line)
        
        if in_paragraph:
            formatted_lines.append('</p>')
        if in_blockquote:
            formatted_lines.append('</blockquote>')
        if in_list:
            formatted_lines.append('</ul>')
        
        content = '\n'.join(formatted_lines)
        
        return content
