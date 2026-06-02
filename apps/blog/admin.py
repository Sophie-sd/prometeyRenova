from django import forms
from django.contrib import admin
from tinymce.widgets import AdminTinyMCE
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateFilter

from .html_sanitize import sanitize_blog_html
from .models import BlogPost


class BlogPostAdminForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = '__all__'
        widgets = {
            'content': AdminTinyMCE(),
        }

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
        if not obj.meta_title:
            obj.meta_title = obj.title[:60]
        if not obj.meta_description:
            obj.meta_description = obj.excerpt[:160]
        if not obj.og_title:
            obj.og_title = obj.title[:60]
        if not obj.og_description:
            obj.og_description = obj.excerpt[:160]
        super().save_model(request, obj, form, change)
