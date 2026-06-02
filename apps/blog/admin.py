from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from tinymce.widgets import AdminTinyMCE
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateFilter

from .html_sanitize import sanitize_blog_html, sanitize_blog_title
from .models import BlogPost

BLOG_SHORT_MCE_ATTRS = {
    'height': 160,
    'min_height': 120,
    'plugins': 'autoresize code',
    'toolbar': 'bold italic underline | removeformat | code',
}


class BlogPostAdminForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = '__all__'
        widgets = {
            'title': AdminTinyMCE(mce_attrs=BLOG_SHORT_MCE_ATTRS),
            'excerpt': AdminTinyMCE(mce_attrs={**BLOG_SHORT_MCE_ATTRS, 'height': 200}),
            'content': AdminTinyMCE(),
        }

    def clean_title(self):
        raw = self.cleaned_data.get('title', '')
        cleaned = sanitize_blog_title(raw)
        if len(cleaned) > BlogPost._meta.get_field('title').max_length:
            raise ValidationError('Заголовок занадто довгий (макс. 200 символів).')
        return cleaned

    def clean_excerpt(self):
        raw = self.cleaned_data.get('excerpt', '')
        cleaned = sanitize_blog_html(raw)
        if len(cleaned) > BlogPost._meta.get_field('excerpt').max_length:
            raise ValidationError('Короткий опис занадто довгий (макс. 300 символів).')
        return cleaned

    def clean_content(self):
        raw = self.cleaned_data.get('content', '')
        return sanitize_blog_html(raw)


@admin.register(BlogPost)
class BlogPostAdmin(UnfoldModelAdmin):
    form = BlogPostAdminForm
    list_filter_sheet = False
    list_display = ['title', 'category', 'is_published', 'created_at', 'reading_time']
    list_filter = [
        ('category', ChoicesDropdownFilter),
        ('is_published', ChoicesDropdownFilter),
        ('created_at', RangeDateFilter),
    ]
    search_fields = ['title', 'content', 'keywords']
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'category', 'featured_image')
        }),
        ('SEO налаштування', {
            'fields': (
                'seo_title', 'seo_description', 'keywords', 'meta_title',
                'meta_description', 'og_title', 'og_description',
            )
        }),
        ('Додаткові налаштування', {
            'fields': ('reading_time', 'is_published')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        from django.utils.html import strip_tags

        plain_title = strip_tags(obj.title or '')
        plain_excerpt = strip_tags(obj.excerpt or '')
        if not obj.meta_title:
            obj.meta_title = plain_title[:60]
        if not obj.meta_description:
            obj.meta_description = plain_excerpt[:160]
        if not obj.og_title:
            obj.og_title = plain_title[:60]
        if not obj.og_description:
            obj.og_description = plain_excerpt[:160]
        super().save_model(request, obj, form, change)
