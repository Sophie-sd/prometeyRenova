"""CMS-вузли вітрини КП: херо-пункти та дерево архітектури."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from .proposal_models import Proposal


class ProposalHighlight(models.Model):
    """Короткий пункт у херо-aside. Порожній список = блок не рендериться."""

    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='highlights',
        verbose_name=_('Пропозиція'),
    )
    title = models.CharField(max_length=200, verbose_name=_('Пункт'))
    title_ru = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Пункт (RU)'),
    )
    title_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Пункт (EN)'),
    )
    title_cs = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Пункт (CS)'),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('order', 'id')
        verbose_name = _('Херо-пункт')
        verbose_name_plural = _('Херо-пункти')

    def __str__(self):
        return self.title

    def get_localized_title(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.title, self.title_ru, self.title_en, self.title_cs)


class ProposalArchNode(models.Model):
    """Вузол дерева архітектури.

    Перший за порядком — корінь. Решта — колонки. Не дублює ProposalSpec.
    """

    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='arch_nodes',
        verbose_name=_('Пропозиція'),
    )
    title = models.CharField(
        max_length=120,
        verbose_name=_('Назва'),
        help_text=_('Перший рядок (найменший порядок) — корінь. Наступні — колонки.'),
    )
    title_ru = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_('Назва (RU)'),
    )
    title_en = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_('Назва (EN)'),
    )
    title_cs = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_('Назва (CS)'),
    )
    caption = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_('Підпис'),
    )
    caption_ru = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_('Підпис (RU)'),
    )
    caption_en = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_('Підпис (EN)'),
    )
    caption_cs = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_('Підпис (CS)'),
    )
    is_accent = models.BooleanField(
        default=False,
        verbose_name=_('Акцент'),
        help_text=_('Помаранчевий акцент колонки (наприклад вітрина).'),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('order', 'id')
        verbose_name = _('Вузол архітектури')
        verbose_name_plural = _('Дерево архітектури')

    def __str__(self):
        return self.title

    def get_localized_title(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.title, self.title_ru, self.title_en, self.title_cs)

    def get_localized_caption(self) -> str:
        from .i18n_content import localized_text

        return localized_text(
            self.caption, self.caption_ru, self.caption_en, self.caption_cs,
        )
