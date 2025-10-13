from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Event, EventCategory, EventRegistration


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color_display', 'event_count']
    list_editable = ['slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            obj.color, obj.color
        )
    color_display.short_description = 'Колір'
    
    def event_count(self, obj):
        return obj.event_set.count()
    event_count.short_description = 'Кількість подій'


class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0
    readonly_fields = ['created_at']
    fields = ['name', 'email', 'phone', 'company', 'is_confirmed', 'created_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'event_type', 'status', 'start_date', 
        'price_display', 'participants_display', 'is_published', 'is_featured'
    ]
    list_filter = [
        'category', 'event_type', 'status', 'is_published', 'is_featured',
        'is_online', 'start_date'
    ]
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['current_participants', 'created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'image')
        }),
        ('Категорія та тип', {
            'fields': ('category', 'event_type', 'status')
        }),
        ('Дати та час', {
            'fields': ('start_date', 'end_date', 'registration_deadline')
        }),
        ('Місце проведення', {
            'fields': ('location', 'is_online', 'meeting_link')
        }),
        ('Ціна та знижки', {
            'fields': ('original_price', 'discount_percent', 'price')
        }),
        ('Обмеження', {
            'fields': ('max_participants', 'current_participants')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description', 'keywords'),
            'classes': ('collapse',)
        }),
        ('Налаштування', {
            'fields': ('is_published', 'is_featured', 'created_at', 'updated_at')
        }),
    )
    
    inlines = [EventRegistrationInline]
    
    def price_display(self, obj):
        if obj.price:
            if obj.discount_percent > 0:
                return format_html(
                    '<span style="text-decoration: line-through; color: #999;">{}</span> '
                    '<span style="color: #E65100; font-weight: bold;">{}</span> '
                    '<span style="background: #E65100; color: white; padding: 1px 4px; font-size: 10px;">-{}%</span>',
                    obj.original_price, obj.price, obj.discount_percent
                )
            return f"{obj.price} грн"
        return "Безкоштовно"
    price_display.short_description = 'Ціна'
    
    def participants_display(self, obj):
        if obj.max_participants:
            return f"{obj.current_participants}/{obj.max_participants}"
        return f"{obj.current_participants}"
    participants_display.short_description = 'Учасники'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')
    
    actions = ['make_published', 'make_unpublished', 'make_featured', 'make_unfeatured']
    
    def make_published(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} подій опубліковано.')
    make_published.short_description = "Опублікувати вибрані події"
    
    def make_unpublished(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} подій знято з публікації.')
    make_unpublished.short_description = "Зняти з публікації"
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} подій відмічено як рекомендовані.')
    make_featured.short_description = "Відмітити як рекомендовані"
    
    def make_unfeatured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} подій знято з рекомендованих.')
    make_unfeatured.short_description = "Зняти з рекомендованих"


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'event', 'phone', 'is_confirmed', 'created_at']
    list_filter = ['is_confirmed', 'created_at', 'event__category']
    search_fields = ['name', 'email', 'phone', 'event__title']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('event', 'name', 'email', 'phone')
        }),
        ('Додаткова інформація', {
            'fields': ('company', 'message')
        }),
        ('Статус', {
            'fields': ('is_confirmed', 'created_at')
        }),
    )
    
    actions = ['confirm_registrations', 'unconfirm_registrations']
    
    def confirm_registrations(self, request, queryset):
        updated = queryset.update(is_confirmed=True)
        self.message_user(request, f'{updated} реєстрацій підтверджено.')
    confirm_registrations.short_description = "Підтвердити вибрані реєстрації"
    
    def unconfirm_registrations(self, request, queryset):
        updated = queryset.update(is_confirmed=False)
        self.message_user(request, f'{updated} реєстрацій знято з підтвердження.')
    unconfirm_registrations.short_description = "Зняти підтвердження" 