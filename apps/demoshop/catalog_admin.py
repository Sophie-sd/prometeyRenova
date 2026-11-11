"""Каталог демо-магазину в адмінці: доступ scoped до власного shop (DemoClient).

Django permissions діють на рівні моделі, не запису. Група DemoClient з
міграції 0002 лишається без цих прав: рядки Permission створює post_migrate
уже після RunPython, а відсутній codename там ковтається. Тому власник
активного магазину проходить через цей mixin, а чужі записи відсікає
`get_queryset`. Звичайний staff без магазину лишається на своїх Django-правах.
"""
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline

from .catalog_models import ShopCategory, ShopProduct, ShopProductImage, ShopReview
from .models import DemoShop


def owned_demo_shop(request):
    """Активний магазин поточного клієнта. Суперюзер і чужий staff — ні."""
    user = getattr(request, 'user', None)
    if not getattr(user, 'is_authenticated', False) or getattr(user, 'is_superuser', False):
        return None
    try:
        shop = user.demo_shop
    except ObjectDoesNotExist:
        return None
    if shop is None or not shop.is_active:
        return None
    return shop


def shop_id_of(obj):
    if obj is None:
        return None
    shop_id = getattr(obj, 'shop_id', None)
    if shop_id is not None:
        return shop_id
    for attr in ('product', 'order'):
        parent = getattr(obj, attr, None)
        nested = getattr(parent, 'shop_id', None)
        if nested is not None:
            return nested
    return None


def owner_matches_shop(request, obj):
    shop = owned_demo_shop(request)
    if shop is None:
        return False
    if obj is None:
        return True
    return shop_id_of(obj) == shop.pk


class ShopScopedAdminMixin:
    """Клієнт (DemoClient) бачить і редагує лише дані свого DemoShop."""

    shop_lookup = 'shop__pk'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        shop = getattr(request.user, 'demo_shop', None)
        if shop is None:
            return qs.none()
        return qs.filter(**{self.shop_lookup: shop.pk})

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'shop' and not request.user.is_superuser:
            shop = getattr(request.user, 'demo_shop', None)
            kwargs['queryset'] = DemoShop.objects.filter(pk=shop.pk) if shop else DemoShop.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not change and getattr(obj, 'shop_id', None) is None:
            shop = getattr(request.user, 'demo_shop', None)
            if shop:
                obj.shop = shop
        super().save_model(request, obj, form, change)

    def _owned_shop(self, request):
        return owned_demo_shop(request)

    def _object_in_shop(self, obj, shop):
        if obj is None:
            return True
        return shop_id_of(obj) == shop.pk

    def _owner_can(self, request, obj=None):
        return owner_matches_shop(request, obj)

    def has_module_permission(self, request):
        if request.user.is_superuser or self._owner_can(request):
            return True
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or self._owner_can(request, obj):
            return True
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or self._owner_can(request, obj):
            return True
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        if request.user.is_superuser or self._owner_can(request):
            return True
        return super().has_add_permission(request)


class ShopNestedInlineMixin:
    """Вкладений рядок видимий лише в магазині батьківського об'єкта.

    `owner_perms` — підмножина задуманої групи DemoClient. Видалення сюди
    не входить: його лишає стандартна перевірка Django-права.
    """

    owner_perms = ('view',)
    shop_lookup = 'shop__pk'

    def has_view_permission(self, request, obj=None):
        if getattr(request.user, 'is_superuser', False):
            return True
        if 'view' in self.owner_perms and owner_matches_shop(request, obj):
            return True
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if getattr(request.user, 'is_superuser', False):
            return True
        if 'change' in self.owner_perms and owner_matches_shop(request, obj):
            return True
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request, obj=None):
        if getattr(request.user, 'is_superuser', False):
            return True
        if 'add' in self.owner_perms and owner_matches_shop(request, obj):
            return True
        return super().has_add_permission(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if getattr(request.user, 'is_superuser', False):
            return qs
        shop = owned_demo_shop(request)
        if shop is None:
            return qs.none()
        return qs.filter(**{self.shop_lookup: shop.pk})


class ShopProductImageInline(ShopNestedInlineMixin, UnfoldTabularInline):
    """Фото: перегляд, додавання, зміна свого товару. Без видалення."""

    owner_perms = ('view', 'add', 'change')
    shop_lookup = 'product__shop__pk'
    model = ShopProductImage
    extra = 0
    fields = ('image', 'alt', 'is_main', 'order')
    ordering = ('-is_main', 'order', 'id')
    verbose_name = _('Фото')
    verbose_name_plural = _('Фото товару')


@admin.register(ShopCategory)
class ShopCategoryAdmin(ShopScopedAdminMixin, UnfoldModelAdmin):
    list_filter_sheet = False
    list_before_template = 'admin/demoshop/_sales_banner.html'
    list_display = ('name', 'shop', 'icon', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'name_ru', 'name_en', 'name_cs')
    ordering = ('shop', 'order')
    fieldsets = (
        (_('Основне'), {'fields': ('shop', 'name', 'name_ru', 'name_en', 'name_cs', 'slug', 'icon')}),
        (_('Видимість'), {'fields': ('is_active', 'order')}),
    )

    def get_list_display(self, request):
        fields = list(super().get_list_display(request))
        if not request.user.is_superuser and 'shop' in fields:
            fields.remove('shop')
        return fields


@admin.register(ShopProduct)
class ShopProductAdmin(ShopScopedAdminMixin, UnfoldModelAdmin):
    list_filter_sheet = False
    list_before_template = 'admin/demoshop/_sales_banner.html'
    inlines = [ShopProductImageInline]
    list_display = ('name', 'shop', 'category', 'price', 'old_price', 'sale_end_date', 'is_active', 'is_featured', 'order')
    list_filter = ('is_active', 'is_featured', 'category')
    search_fields = ('name', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('shop', 'order')
    fieldsets = (
        (_('Основне'), {'fields': (
            'shop', 'category', 'name', 'name_ru', 'name_en', 'name_cs', 'slug',
            'short_description', 'short_description_ru', 'short_description_en', 'short_description_cs',
            'description', 'description_ru', 'description_en', 'description_cs',
        )}),
        (_('Ціна та акція'), {'fields': (
            'price', 'old_price', 'sale_end_date',
            'gift_promo_text', 'gift_promo_text_ru', 'gift_promo_text_en', 'gift_promo_text_cs',
        )}),
        (_('Видимість'), {'fields': ('is_active', 'is_featured', 'order')}),
    )

    def get_list_display(self, request):
        fields = list(super().get_list_display(request))
        if not request.user.is_superuser and 'shop' in fields:
            fields.remove('shop')
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category' and not request.user.is_superuser:
            shop = getattr(request.user, 'demo_shop', None)
            kwargs['queryset'] = ShopCategory.objects.filter(shop=shop) if shop else ShopCategory.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.is_superuser:
            return fieldsets
        return tuple(
            (title, {**opts, 'fields': tuple(f for f in opts['fields'] if f != 'shop')})
            for title, opts in fieldsets
        )


@admin.register(ShopReview)
class ShopReviewAdmin(ShopScopedAdminMixin, UnfoldModelAdmin):
    list_filter_sheet = False
    list_before_template = 'admin/demoshop/_sales_banner.html'
    list_display = ('author_name', 'shop', 'product', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    search_fields = ('author_name', 'text')
    ordering = ('-created_at',)

    def get_list_display(self, request):
        fields = list(super().get_list_display(request))
        if not request.user.is_superuser and 'shop' in fields:
            fields.remove('shop')
        return fields
