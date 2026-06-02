"""Додаткові фільтри changelist для Unfold (випадаючі списки)."""
from collections.abc import Generator
from typing import Any

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.utils.translation import gettext_lazy as _

from unfold.contrib.filters.admin.mixins import DropdownMixin, ValueMixin


class BooleanDropdownFilter(ValueMixin, DropdownMixin, admin.BooleanFieldListFilter):
    """Булевий фільтр як select замість горизонтальних кнопок."""

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None

        if add_facets:
            choices = [
                self.all_option,
                ("1", f"{_('Yes')} ({facet_counts['true__c']})"),
                ("0", f"{_('No')} ({facet_counts['false__c']})"),
            ]
        else:
            choices = [
                self.all_option,
                ("1", _("Yes")),
                ("0", _("No")),
            ]

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value()},
                multiple=False,
            ),
        }
