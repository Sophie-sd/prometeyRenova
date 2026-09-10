"""Permission callbacks для UNFOLD sidebar (config/settings.py).

Узагальнена логіка (одна функція на тип демо-тенанта + `is_prometey_staff`,
що виключає всі типи) живе в `apps.demotenant.permissions`. Тут — тонкий
реекспорт, щоб не змінювати рядки `UNFOLD["SIDEBAR"]` у `config/settings.py`,
які й далі посилаються на `apps.demoshop.admin_permissions.is_demo_client`
і `apps.demoshop.admin_permissions.is_prometey_staff`.
"""
from apps.demotenant.permissions import is_demo_shop_client as is_demo_client  # noqa: F401
from apps.demotenant.permissions import is_prometey_staff  # noqa: F401
