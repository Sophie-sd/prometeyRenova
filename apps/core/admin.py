from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.actions import delete_selected
from django.contrib.auth.models import Group
from datetime import timedelta
import csv
from django.http import HttpResponse
from .models import FormSubmission, ArchivedFormSubmission, InProgressFormSubmission, CompletedFormSubmission


# ===== ВИДАЛЕННЯ ГРУП З ADMIN =====
admin.site.unregister(Group)



@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    """CRM система управління заявками з кольоровим кодуванням та статистикою"""
    
    # ===== ОСНОВНА КОНФІГУРАЦІЯ =====
    list_display = [
        'id_badge', 'project_display', 'name_display', 'phone_display', 
        'form_type_badge', 'status', 'priority_badge', 'created_at_display', 
        'time_elapsed', 'assigned_to_display'
    ]
    
    list_filter = [
        'status', 
        'form_type', 
        'priority', 
        ('created_at', admin.DateFieldListFilter),
        'assigned_to'
    ]
    
    search_fields = ['name', 'phone', 'email', 'details', 'manager_comment', 'project']
    readonly_fields = [
        'created_at', 'updated_at', 'ip_address', 'user_agent', 
        'priority_badge'
    ]
    
    list_editable = ['status']
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    # ===== FIELDSETS ДЛЯ ДЕТАЛЕЙ =====
    fieldsets = (
        (_('Контактна інформація'), {
            'fields': ('name', 'phone', 'email', 'messenger_link')
        }),
        (_('Класифікація'), {
            'fields': ('project', 'form_type', 'status', 'priority', 'assigned_to'),
            'classes': ('wide',)
        }),
        (_('Деталі заявки'), {
            'fields': ('details',),
            'classes': ('wide',)
        }),
        (_('Робота менеджера'), {
            'fields': ('manager_comment',),
            'classes': ('wide',)
        }),
        (_('Системна інформація'), {
            'fields': ('created_at', 'updated_at', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        })
    )
    
    # ===== ДІЇ (ACTIONS) =====
    actions = [
        delete_selected,
        'mark_as_in_progress', 
        'mark_as_thinking',
        'mark_as_no_contact',
        'mark_as_ordered',
        'mark_as_completed',
        'mark_as_rejected',
        'assign_to_me',
        'remove_assignment',
        'set_high_priority',
        'set_normal_priority',
        'set_low_priority',
        'export_as_csv'
    ]
    
    # ===== СТИЛІ =====
    class Media:
        css = {
            'all': ['admin/css/form_submissions_colors.css']
        }
    
    # ===== МЕТОДИ DISPLAY =====
    
    def id_badge(self, obj):
        """ID з малюнком"""
        return format_html(
            '<span style="background-color: #e8e8e8; padding: 4px 8px; '
            'border-radius: 4px; font-family: monospace; font-weight: bold;">#{}</span>',
            obj.id
        )
    id_badge.short_description = 'ID'
    
    def name_display(self, obj):
        """Ім'я з перевіркою на довгі значення"""
        return obj.name[:30] + '...' if len(obj.name) > 30 else obj.name
    name_display.short_description = _('Ім\'я')
    
    def phone_display(self, obj):
        """Телефон як посилання"""
        return format_html(
            '<a href="tel:{}" style="text-decoration: none;">{}</a>',
            obj.phone, obj.phone
        )
    phone_display.short_description = _('Телефон')
    
    def project_display(self, obj):
        """Проект — короткий опис або тире якщо порожнє"""
        if obj.project:
            return obj.project[:50] + '...' if len(obj.project) > 50 else obj.project
        return '—'
    project_display.short_description = _('Проект')
    
    def form_type_badge(self, obj):
        """Тип форми з малюнком"""
        # Обробка порожнього form_type для старих записів
        form_type = obj.form_type or 'manual'
        
        colors = {
            'manual': '#9E9E9E',
            'site-request': '#FF6B6B',
            'developer': '#4ECDC4',
            'consultation': '#45B7D1',
            'contact': '#FFA07A',
            'call-request': '#98D8C8',
            'footer-consultation': '#F7DC6F',
            'event_registration': '#BB8FCE',
            'test_result': '#85C1E2',
        }
        color = colors.get(form_type, '#999999')
        
        # Отримуємо текст відображення, якщо не знаходимо — розглядаємо як manual
        display_text = obj.get_form_type_display_uk() if obj.form_type else 'Ручна'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color, display_text
        )
    form_type_badge.short_description = _('Тип форми')
    
    def status_badge(self, obj):
        """Статус з кольором та текстом"""
        color = obj.get_status_color()
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 6px 12px; '
            'border-radius: 12px; font-weight: bold; display: inline-block;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = _('Статус')
    
    def priority_badge(self, obj):
        """Пріоритет з відповідним кольором"""
        colors = {
            'high': '#DC3545',      # Червоний
            'normal': '#FFC107',    # Жовтий
            'low': '#28A745'        # Зелений
        }
        color = colors.get(obj.priority, '#999999')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = _('Пріоритет')
    
    def created_at_display(self, obj):
        """Дата створення в форматованому вигляді"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
    created_at_display.short_description = _('Дата')
    
    def time_elapsed(self, obj):
        """Час з моменту створення"""
        return obj.time_since_created()
    time_elapsed.short_description = _('Минуло')
    
    def is_urgent_indicator(self, obj):
        """Індикатор критичних заявок"""
        if obj.is_urgent():
            return format_html(
                '<span style="color: white; background-color: red; '
                'padding: 4px 8px; border-radius: 4px; font-weight: bold; '
                'display: inline-block;">⚠️ КРИТИЧНО</span>'
            )
        return '—'
    is_urgent_indicator.short_description = _('Критично')
    
    def assigned_to_display(self, obj):
        """Відображення призначення"""
        if obj.assigned_to:
            return format_html(
                '<span style="background-color: #d4edda; color: #155724; '
                'padding: 4px 8px; border-radius: 4px;">{}</span>',
                obj.assigned_to.get_full_name() or obj.assigned_to.username
            )
        return format_html(
            '<span style="color: #999;">—</span>'
        )
    assigned_to_display.short_description = _('Призначено')
    
    def extra_data_formatted(self, obj):
        """Форматований вивід додаткових даних"""
        if not obj.extra_data:
            return '—'
        
        import json
        try:
            formatted = json.dumps(obj.extra_data, indent=2, ensure_ascii=False)
            return format_html('<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px;">{}</pre>', formatted)
        except:
            return str(obj.extra_data)
    extra_data_formatted.short_description = _('Додаткові дані')
    
    # ===== ДІЇ =====
    
    def mark_as_in_progress(self, request, queryset):
        """Перевести в роботу"""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'✓ {updated} заявок переведено в роботу.')
    mark_as_in_progress.short_description = "➜ Перевести в роботу"
    
    def mark_as_thinking(self, request, queryset):
        """Позначити як 'Думає'"""
        updated = queryset.update(status='thinking')
        self.message_user(request, f'✓ {updated} заявок позначено як "Думає".')
    mark_as_thinking.short_description = "⏸ Позначити як 'Думає'"
    
    def mark_as_no_contact(self, request, queryset):
        """Позначити як 'Не на зв'язку'"""
        updated = queryset.update(status='no_contact')
        self.message_user(request, f'✓ {updated} заявок позначено як "Не на зв\'язку".')
    mark_as_no_contact.short_description = "❌ Позначити як 'Не на зв'язку'"
    
    def mark_as_ordered(self, request, queryset):
        """Позначити як 'Замовив сайт'"""
        updated = queryset.update(status='ordered')
        self.message_user(request, f'✓ {updated} заявок позначено як "Замовив сайт". Вітаємо! 🎉')
    mark_as_ordered.short_description = "✅ Позначити як 'Замовив сайт' (успіх!)"
    
    def mark_as_completed(self, request, queryset):
        """Позначити як 'Завершено'"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'✓ {updated} заявок позначено як «Завершено». Розробку завершено! 🎉')
    mark_as_completed.short_description = "✅ Позначити як «Завершено»"
    
    def mark_as_rejected(self, request, queryset):
        """Позначити як 'Відмова'"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'✓ {updated} заявок позначено як "Відмова".')
    mark_as_rejected.short_description = "🗑 Позначити як 'Відмова'"
    
    def assign_to_me(self, request, queryset):
        """Призначити на себе"""
        updated = queryset.update(assigned_to=request.user)
        self.message_user(request, f'✓ {updated} заявок призначено на вас.')
    assign_to_me.short_description = "👤 Призначити на мене"
    
    def remove_assignment(self, request, queryset):
        """Зняти призначення"""
        updated = queryset.update(assigned_to=None)
        self.message_user(request, f'✓ Призначення знято для {updated} заявок.')
    remove_assignment.short_description = "👤❌ Зняти призначення"
    
    def set_high_priority(self, request, queryset):
        """Встановити високий пріоритет"""
        updated = queryset.update(priority='high')
        self.message_user(request, f'✓ {updated} заявок встановлено високий пріоритет.')
    set_high_priority.short_description = "🔴 Встановити ВИСОКИЙ пріоритет"
    
    def set_normal_priority(self, request, queryset):
        """Встановити нормальний пріоритет"""
        updated = queryset.update(priority='normal')
        self.message_user(request, f'✓ {updated} заявок встановлено нормальний пріоритет.')
    set_normal_priority.short_description = "🟡 Встановити нормальний пріоритет"
    
    def set_low_priority(self, request, queryset):
        """Встановити низький пріоритет"""
        updated = queryset.update(priority='low')
        self.message_user(request, f'✓ {updated} заявок встановлено низький пріоритет.')
    set_low_priority.short_description = "🟢 Встановити низький пріоритет"
    
    def export_as_csv(self, request, queryset):
        """Експорт в CSV"""
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="submissions_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        # Додаємо BOM для правильного кодування в Excel
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        # Заголовок
        writer.writerow([
            'ID', 'Ім\'я', 'Телефон', 'Email', 'Тип форми', 'Статус', 
            'Пріоритет', 'Дата', 'Деталі', 'Коментар менеджера', 'Призначено'
        ])
        
        # Дані
        for submission in queryset:
            writer.writerow([
                submission.id,
                submission.name,
                submission.phone,
                submission.email,
                submission.get_form_type_display(),
                submission.get_status_display(),
                submission.get_priority_display(),
                submission.created_at.strftime('%d.%m.%Y %H:%M'),
                submission.details[:100] if submission.details else '',
                submission.manager_comment[:100] if submission.manager_comment else '',
                str(submission.assigned_to) if submission.assigned_to else ''
            ])
        
        self.message_user(request, f'✓ Експортовано {queryset.count()} заявок у CSV.')
        return response
    export_as_csv.short_description = "📊 Експортувати у CSV"
    
    # ===== CHANGELIST VIEW З СТАТИСТИКОЮ =====
    
    def changelist_view(self, request, extra_context=None):
        """Додаємо статистику в changelist"""
        extra_context = extra_context or {}
        
        # Загальна статистика
        total_count = FormSubmission.objects.count()
        
        # Статистика по статусах
        status_stats = FormSubmission.objects.values('status').annotate(
            count=models.Count('id')
        ).order_by('status')
        
        # Критичні заявки (>24 години в статусі 'new')
        urgent_count = FormSubmission.objects.filter(
            status='new',
            created_at__lt=timezone.now() - timedelta(hours=24)
        ).count()
        
        # Заявки без призначення
        unassigned_count = FormSubmission.objects.filter(assigned_to__isnull=True).count()
        
        # Успішні угоди (статус 'ordered') за останній місяць
        one_month_ago = timezone.now() - timedelta(days=30)
        ordered_this_month = FormSubmission.objects.filter(
            status='ordered',
            updated_at__gte=one_month_ago
        ).count()
        
        extra_context.update({
            'total_count': total_count,
            'status_stats': status_stats,
            'urgent_count': urgent_count,
            'unassigned_count': unassigned_count,
            'ordered_this_month': ordered_this_month,
        })
        
        return super().changelist_view(request, extra_context)
    
    # ===== ВИДАЛЕННЯ =====
    
    def delete_queryset(self, request, queryset):
        """Гарантує коректне bulk-видалення заявок з логуванням."""
        count, deleted_by_model = queryset.delete()
        self.message_user(
            request, 
            _('Видалено %(count)d заявок.') % {'count': count}, 
            messages.SUCCESS
        )
    
    def delete_model(self, request, obj):
        """Гарантує коректне одиночне видалення заявки."""
        super().delete_model(request, obj)
        self.message_user(
            request, 
            _('Заявку видалено.'), 
            messages.SUCCESS
        )
    
    # ===== QUERYSET ОПТИМІЗАЦІЯ =====
    
    def get_queryset(self, request):
        """Оптимізація для змешування з assign_to та уникнення N+1. Виключає архівовані та завершені заявки, а також ті, що в роботі."""
        qs = super().get_queryset(request)
        return qs.exclude(status__in=['rejected', 'in_progress', 'completed']).select_related('assigned_to')
    
    def get_changeform_initial_data(self, request):
        """Встановлює замовчування для нових заявок при додаванні через адмінку"""
        initial = super().get_changeform_initial_data(request)
        initial['form_type'] = 'manual'
        return initial


@admin.register(ArchivedFormSubmission)
class ArchivedFormSubmissionAdmin(FormSubmissionAdmin):
    """Admin для архівованих заявок (status=rejected)"""
    
    def get_queryset(self, request):
        """Показує тільки архівовані заявки (status=rejected)"""
        # Викликаємо super().get_queryset() від admin.ModelAdmin, щоб обійти фільтр exclude(status='rejected')
        # з FormSubmissionAdmin.get_queryset()
        qs = admin.ModelAdmin.get_queryset(self, request)
        return qs.filter(status='rejected').select_related('assigned_to')


@admin.register(InProgressFormSubmission)
class InProgressFormSubmissionAdmin(FormSubmissionAdmin):
    """Admin для заявок у статусі «В роботі»"""
    
    def get_queryset(self, request):
        """Показує тільки заявки у статусі «В роботі»"""
        qs = admin.ModelAdmin.get_queryset(self, request)
        return qs.filter(status='in_progress').select_related('assigned_to')


@admin.register(CompletedFormSubmission)
class CompletedFormSubmissionAdmin(FormSubmissionAdmin):
    """Admin для завершених заявок"""
    
    def get_queryset(self, request):
        """Показує тільки завершені заявки"""
        qs = admin.ModelAdmin.get_queryset(self, request)
        return qs.filter(status='completed').select_related('assigned_to')
