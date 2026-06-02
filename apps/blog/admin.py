from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(UnfoldModelAdmin):
    list_display = ['title', 'category', 'is_published', 'created_at', 'reading_time']
    list_filter = ['category', 'is_published', 'created_at']
    search_fields = ['title', 'content', 'keywords']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'category', 'featured_image')
        }),
        ('SEO налаштування', {
            'fields': ('seo_title', 'seo_description', 'keywords', 'meta_title', 'meta_description', 'og_title', 'og_description')
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
