from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class BlogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    excerpt = models.TextField(max_length=300, verbose_name="Короткий опис")
    content = models.TextField(verbose_name="Контент")
    seo_title = models.CharField(max_length=70, verbose_name="SEO заголовок")
    seo_description = models.CharField(max_length=160, verbose_name="SEO опис")
    keywords = models.CharField(max_length=255, verbose_name="Ключові слова")
    
    # Нові поля для SEO
    meta_title = models.CharField(max_length=60, verbose_name="Meta Title", blank=True)
    meta_description = models.CharField(max_length=160, verbose_name="Meta Description", blank=True)
    og_title = models.CharField(max_length=60, verbose_name="OG Title", blank=True)
    og_description = models.CharField(max_length=160, verbose_name="OG Description", blank=True)
    
    # Додаткові поля
    reading_time = models.PositiveIntegerField(default=5, verbose_name="Час читання (хв)")
    featured_image = models.ImageField(upload_to='blog/', verbose_name="Головне зображення", blank=True)
    category = models.CharField(max_length=50, choices=[
        ('web-development', 'Веб-розробка'),
        ('courses', 'Курси програмування'),
        ('telegram-bots', 'Telegram боти'),
        ('business', 'Бізнес'),
        ('technology', 'Технології'),
        ('ai-development', 'AI розробка'),
        ('ai-agents', 'AI агенти'),
        ('ai-automation', 'AI автоматизація'),
    ], default='web-development', verbose_name="Категорія")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")
    is_published = models.BooleanField(default=True, verbose_name="Опубліковано")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Стаття блогу"
        verbose_name_plural = "Статті блогу"
    
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
