"""Unfold-розділ «Імпорт КП»: завантаження пакета, шаблони, інструкція, soft-delete/restore, rollback."""
from pathlib import Path

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from .proposal_admin import ProposalAdmin
from .proposal_import import (
    MAX_ZIP_BYTES, ImportError_, can_import, import_proposal_package, restore_proposal,
    rollback_import, soft_delete_proposal,
)
from .proposal_models import Proposal, ProposalImport

KP_TEMPLATES_DIR = Path(__file__).resolve().parent / 'kp_templates'
TEMPLATE_FILES = {
    'landing': 'template-landing.zip',
    'shop': 'template-shop.zip',
    'corporate': 'template-corporate.zip',
    'corporate_catalog': 'template-corporate-catalog.zip',
    'instruction': 'INSTRUCTION.md',
}
TEMPLATE_LABELS = {
    'landing': 'Шаблон: лендінг', 'shop': 'Шаблон: інтернет-магазин', 'corporate': 'Шаблон: корпоративний',
    'corporate_catalog': 'Шаблон: корпоративний з каталогом', 'instruction': 'Інструкція (INSTRUCTION.md)',
}


def import_enabled() -> bool:
    return bool(getattr(settings, 'PROPOSAL_IMPORT_ENABLED', False))


def _guard(request):
    if not import_enabled():
        raise PermissionDenied('Імпорт КП вимкнено (PROPOSAL_IMPORT_ENABLED=False)')
    if not can_import(request.user):
        raise PermissionDenied('Немає права core.can_import_proposal')


class UploadForm(forms.Form):
    package = forms.FileField(label='Пакет КП (.zip)')

    def clean_package(self):
        f = self.cleaned_data['package']
        if f.size > MAX_ZIP_BYTES:
            raise forms.ValidationError('Zip більше 20 МБ')
        if not f.name.lower().endswith('.zip'):
            raise forms.ValidationError('Потрібен .zip')
        return f


class SoftDeleteForm(forms.Form):
    slug = forms.CharField(label='Введіть slug КП для підтвердження')
    confirm = forms.BooleanField(label='Розумію: КП буде знято з публікації, демо імпортованого КП — вимкнено')

    def __init__(self, *args, expected_slug='', **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_slug = expected_slug

    def clean_slug(self):
        v = self.cleaned_data['slug'].strip()
        if v != self.expected_slug:
            raise forms.ValidationError('Slug не збігається')
        return v


@admin.register(ProposalImport)
class ProposalImportAdmin(UnfoldModelAdmin):
    list_display = ('id', 'proposal', 'kind', 'version', 'status', 'original_name', 'user', 'created_at')
    list_filter = ('kind', 'status')
    search_fields = ('proposal__slug', 'original_name', 'sha256')
    readonly_fields = [f.name for f in ProposalImport._meta.fields]
    actions = ['rollback_action']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        info = self.opts.app_label, self.opts.model_name
        return [
            path('upload/', self.admin_site.admin_view(self.upload_view), name='%s_%s_upload' % info),
            path('template/<str:key>/', self.admin_site.admin_view(self.template_view), name='%s_%s_template' % info),
            path('proposal/<int:pk>/soft-delete/', self.admin_site.admin_view(self.soft_delete_view),
                 name='%s_%s_soft_delete' % info),
        ] + super().get_urls()

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'Імпорт КП'
        if import_enabled() and can_import(request.user):
            messages.info(request, 'Завантажити пакет: ' + reverse('admin:core_proposalimport_upload'))
        return super().changelist_view(request, extra_context)

    def _downloads(self):
        return [(TEMPLATE_LABELS[k], reverse('admin:core_proposalimport_template', args=[k])) for k in TEMPLATE_FILES]

    def upload_view(self, request):
        _guard(request)
        form = UploadForm(request.POST or None, request.FILES or None)
        if request.method == 'POST' and form.is_valid():
            f = form.cleaned_data['package']
            try:
                rec = import_proposal_package(f.read(), user=request.user, original_name=f.name)
            except ImportError_ as exc:
                messages.error(request, f'Імпорт не виконано: {exc}')
            else:
                messages.success(request, f'Імпортовано КП «{rec.proposal.slug}», версія {rec.version}. '
                                          'Опубліковано: ' + ('так' if rec.proposal.is_published else 'ні'))
                return HttpResponseRedirect(reverse('admin:core_proposal_change', args=[rec.proposal.pk]))
        ctx = {**self.admin_site.each_context(request), 'title': 'Імпорт КП — Завантажить пакет', 'form': form,
               'submit_label': 'Завантажить пакет', 'downloads': self._downloads(), 'opts': self.opts}
        return TemplateResponse(request, 'admin/core/proposalimport/form.html', ctx)

    def template_view(self, request, key):
        if not request.user.is_staff:
            raise PermissionDenied
        name = TEMPLATE_FILES.get(key)
        if not name:
            raise Http404
        fp = KP_TEMPLATES_DIR / name
        if not fp.exists():
            raise Http404
        ctype = 'application/zip' if name.endswith('.zip') else 'text/markdown; charset=utf-8'
        resp = FileResponse(fp.open('rb'), as_attachment=True, filename=name, content_type=ctype)
        resp['X-Content-Type-Options'] = 'nosniff'
        return resp

    def soft_delete_view(self, request, pk):
        _guard(request)
        proposal = get_object_or_404(Proposal, pk=pk)
        form = SoftDeleteForm(request.POST or None, expected_slug=proposal.slug)
        if request.method == 'POST' and form.is_valid():
            soft_delete_proposal(proposal, user=request.user)
            messages.success(request, f'КП «{proposal.slug}» мʼяко видалено (можна відновити).')
            return HttpResponseRedirect(reverse('admin:core_proposal_changelist'))
        ctx = {**self.admin_site.each_context(request), 'title': f'Мʼяке видалення КП «{proposal.slug}»',
               'intro': 'Дані не видаляються: КП знімається з публікації. Стандартне демо не змінюється.',
               'form': form, 'submit_label': 'Видалити (soft)', 'opts': self.opts}
        return TemplateResponse(request, 'admin/core/proposalimport/form.html', ctx)

    @admin.action(description=_('Відкотити (новий імпорт kind=rollback)'))
    def rollback_action(self, request, queryset):
        _guard(request)
        for rec in queryset:
            try:
                new = rollback_import(rec, user=request.user)
            except ImportError_ as exc:
                self.message_user(request, f'#{rec.pk}: {exc}', messages.ERROR)
            else:
                self.message_user(request, f'#{rec.pk}: відкат виконано, нова версія {new.version}', messages.SUCCESS)


@admin.action(description=_('Мʼяко видалити (з підтвердженням slug)'))
def soft_delete_action(modeladmin, request, queryset):
    _guard(request)
    if queryset.count() != 1:
        modeladmin.message_user(request, 'Оберіть рівно одне КП', messages.WARNING)
        return None
    return HttpResponseRedirect(reverse('admin:core_proposalimport_soft_delete', args=[queryset.first().pk]))


@admin.action(description=_('Відновити мʼяко видалені'))
def restore_action(modeladmin, request, queryset):
    _guard(request)
    n = 0
    for p in queryset.filter(deleted_at__isnull=False):
        restore_proposal(p)
        n += 1
    modeladmin.message_user(request, f'Відновлено: {n}', messages.SUCCESS)


@admin.action(description=_('Імпорт КП: завантажить пакет'))
def upload_redirect_action(modeladmin, request, queryset):
    _guard(request)
    return HttpResponseRedirect(reverse('admin:core_proposalimport_upload'))


_orig_get_actions = ProposalAdmin.get_actions


def _get_actions(self, request):
    actions = _orig_get_actions(self, request)
    if import_enabled() and can_import(request.user):
        for fn in (soft_delete_action, restore_action, upload_redirect_action):
            actions[fn.__name__] = (fn, fn.__name__, fn.short_description)
    return actions


ProposalAdmin.get_actions = _get_actions
