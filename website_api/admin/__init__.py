from django.contrib import admin
from django import forms
from website_api.models import (
    City, Service, TechnicCategory, Option, OptionPrice,
    CityContent, ServiceContent, Advantage, Metric,
    Contact, AppLink, SeoMeta, Lead,
    ParameterType, ParameterValue, OptionParameterType,
    ParameterPrice, DeliveryZone, PriceChangeLog, Document
)
from website_api.forms import CityContentAdminForm, ServiceContentAdminForm, DocumentAdminForm
from website_api.cache import pricing_cache


class CityContentInline(admin.StackedInline):
    model = CityContent
    form = CityContentAdminForm
    extra = 0
    fieldsets = (
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'h1_title')
        }),
        ('Контент (HTML)', {
            'fields': ('short_description', 'full_description', 'advantages_html'),
            'description': 'Используйте HTML редактор для форматирования контента'
        }),
        ('Статистика (обновляется автоматически)', {
            'fields': ('partner_count', 'avg_rating', 'review_count'),
            'classes': ('collapse',)
        }),
    )
    
    @property
    def media(self):
        """Подключаем Media для CKEditor виджетов"""
        media = super().media
        # Добавляем media от формы с CKEditor виджетами
        if self.form:
            media = media + self.form().media
        return media


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CityContentInline]
    
    @property
    def media(self):
        """Подключаем Media для CKEditor виджетов из inline форм"""
        media = super().media
        for inline in self.inlines:
            if hasattr(inline, 'form') and inline.form:
                media = media + inline.form().media
        return media


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(TechnicCategory)
class TechnicCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    search_fields = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}


class OptionParameterTypeInline(admin.TabularInline):
    """Inline для параметров опции"""
    model = OptionParameterType
    extra = 1
    fields = ['parameter_type', 'is_required']
    autocomplete_fields = ['parameter_type']


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ['title', 'service', 'has_parameters', 'is_active']
    list_filter = ['service', 'has_parameters', 'is_active']
    search_fields = ['title', 'description']
    inlines = [OptionParameterTypeInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'service', 'description')
        }),
        ('Параметры ценообразования', {
            'fields': ('has_parameters',),
            'description': 'Если включено, цена будет зависеть от выбранных параметров'
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
    )


@admin.register(OptionPrice)
class OptionPriceAdmin(admin.ModelAdmin):
    list_display = ['option', 'city', 'technic_category', 'amount']
    list_filter = ['city', 'option__service']
    search_fields = ['option__title', 'city__title']
    
    def save_model(self, request, obj, form, change):
        """Логирование изменений цен"""
        if change:
            old_obj = OptionPrice.objects.get(pk=obj.pk)
            old_amount = old_obj.amount
        else:
            old_amount = None
        
        # Сохраняем объект
        super().save_model(request, obj, form, change)
        
        # Логируем изменение, если цена изменилась
        if change and old_amount != obj.amount:
            PriceChangeLog.objects.create(
                entity_type='OPTION_PRICE',
                entity_id=obj.pk,
                entity_description=str(obj),
                old_value=old_amount,
                new_value=obj.amount,
                changed_by=request.user.email or request.user.username,
            )
        elif not change:
            # Создание новой записи
            PriceChangeLog.objects.create(
                entity_type='OPTION_PRICE',
                entity_id=obj.pk,
                entity_description=str(obj),
                old_value=None,
                new_value=obj.amount,
                changed_by=request.user.email or request.user.username,
            )
        
        # Инвалидируем кэш
        pricing_cache.invalidate()


@admin.register(ServiceContent)
class ServiceContentAdmin(admin.ModelAdmin):
    form = ServiceContentAdminForm
    list_display = ['service', 'city', 'updated_at']
    list_filter = ['service', 'city']
    search_fields = ['service__title', 'city__title', 'meta_title']
    
    @property
    def media(self):
        """Подключаем Media для CKEditor виджетов"""
        media = super().media
        if self.form:
            media = media + self.form().media
        return media
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('service', 'city'),
            'description': 'Если город не выбран - контент будет общим для всех городов'
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'h1_title')
        }),
        ('Контент (HTML)', {
            'fields': ('short_description', 'description', 'how_it_works_html', 'benefits_html'),
            'description': 'Используйте HTML редактор для форматирования контента'
        }),
        ('Медиа', {
            'fields': ('icon_url', 'cover_image_url'),
            'classes': ('collapse',),
            'description': 'URL-адреса изображений (относительные или абсолютные)'
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('service', 'city')


@admin.register(Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_audience', 'display_order', 'is_active']
    list_filter = ['target_audience', 'is_active']
    list_editable = ['display_order']


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ['display_label', 'value', 'metric_type', 'is_visible_on_site', 'last_updated']
    list_filter = ['metric_type', 'is_visible_on_site']
    search_fields = ['metric_key', 'display_label']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['label', 'contact_type', 'value', 'display_order', 'is_active']
    list_filter = ['contact_type', 'is_active']
    list_editable = ['display_order']


@admin.register(AppLink)
class AppLinkAdmin(admin.ModelAdmin):
    list_display = ['platform', 'app_type', 'version', 'is_active']
    list_filter = ['platform', 'app_type', 'is_active']


@admin.register(SeoMeta)
class SeoMetaAdmin(admin.ModelAdmin):
    list_display = ['page_type', 'full_slug', 'city', 'service', 'is_active']
    list_filter = ['page_type', 'is_active']
    search_fields = ['full_slug', 'title']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Админка для документов (политика конфиденциальности, оферта и т.д.)"""
    form = DocumentAdminForm
    list_display = ['title', 'slug', 'version', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'slug', 'meta_title']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'version', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'h1_title')
        }),
        ('Контент (HTML)', {
            'fields': ('short_description', 'full_description'),
            'description': 'Используйте HTML редактор для форматирования контента'
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @property
    def media(self):
        """Подключаем Media для CKEditor виджетов"""
        media = super().media
        if self.form:
            media = media + self.form().media
        return media


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['display_link', 'phone', 'lead_type', 'city', 'service', 'status', 'created_at']
    list_display_links = ['display_link']
    list_filter = ['status', 'lead_type', 'city', 'service', 'created_at']
    search_fields = ['name', 'phone', 'email', 'page_url']
    readonly_fields = ['created_at', 'processed_at']
    fieldsets = (
        ('Данные клиента', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Тип и содержание заявки', {
            'fields': ('lead_type', 'city', 'service', 'message')
        }),
        ('Информация о странице', {
            'fields': ('page_url', 'source_page', 'utm_source', 'utm_medium', 'utm_campaign')
        }),
        ('Статус обработки', {
            'fields': ('status', 'created_at', 'processed_at')
        }),
    )
    
    actions = ['mark_as_processing']
    
    def display_link(self, obj):
        """Отображает имя или телефон с коротким ID для кликабельности"""
        if obj.name and obj.name.strip():
            return f"{obj.name} (#{obj.id})"
        return f"{obj.phone} (#{obj.id})"
    display_link.short_description = "Имя / Телефон"
    display_link.admin_order_field = 'name'
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_as_processing.short_description = "Отметить как обработано"


# ============== Pricing System Admin ==============

class ParameterValueInline(admin.TabularInline):
    """Inline для значений параметра"""
    model = ParameterValue
    extra = 3
    fields = ['value', 'display_name', 'sort_order', 'is_active']


@admin.register(ParameterType)
class ParameterTypeAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'values_count', 'sort_order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'code']
    inlines = [ParameterValueInline]
    fieldsets = (
        (None, {
            'fields': ('code', 'title', 'description')
        }),
        ('Настройки', {
            'fields': ('sort_order', 'is_active')
        }),
    )
    
    def values_count(self, obj):
        return obj.values.filter(is_active=True).count()
    values_count.short_description = 'Кол-во значений'


@admin.register(ParameterValue)
class ParameterValueAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'parameter_type', 'value', 'sort_order', 'is_active']
    list_filter = ['parameter_type', 'is_active']
    search_fields = ['display_name', 'value']
    autocomplete_fields = ['parameter_type']


@admin.register(OptionParameterType)
class OptionParameterTypeAdmin(admin.ModelAdmin):
    list_display = ['option', 'parameter_type', 'is_required']
    list_filter = ['is_required', 'parameter_type']
    search_fields = ['option__title', 'parameter_type__title']
    autocomplete_fields = ['option', 'parameter_type']


@admin.register(ParameterPrice)
class ParameterPriceAdmin(admin.ModelAdmin):
    list_display = ['option', 'parameter_value', 'city', 'technic_category', 'price_modifier']
    list_filter = ['city', 'option__service', 'parameter_value__parameter_type']
    search_fields = ['option__title', 'parameter_value__display_name']
    autocomplete_fields = ['option', 'parameter_value', 'city', 'technic_category']
    
    def save_model(self, request, obj, form, change):
        """Логирование изменений цен"""
        if change:
            old_obj = ParameterPrice.objects.get(pk=obj.pk)
            old_value = old_obj.price_modifier
        else:
            old_value = None
        
        # Сохраняем объект
        super().save_model(request, obj, form, change)
        
        # Логируем изменение, если цена изменилась
        if change and old_value != obj.price_modifier:
            PriceChangeLog.objects.create(
                entity_type='PARAMETER_PRICE',
                entity_id=obj.pk,
                entity_description=str(obj),
                old_value=old_value,
                new_value=obj.price_modifier,
                changed_by=request.user.email or request.user.username,
            )
        elif not change:
            # Создание новой записи
            PriceChangeLog.objects.create(
                entity_type='PARAMETER_PRICE',
                entity_id=obj.pk,
                entity_description=str(obj),
                old_value=None,
                new_value=obj.price_modifier,
                changed_by=request.user.email or request.user.username,
            )
        
        # Инвалидируем кэш
        pricing_cache.invalidate()


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ['city', 'zone_name', 'location_status', 'delivery_price', 'is_active']
    list_filter = ['city', 'location_status', 'is_active']
    search_fields = ['zone_name', 'city__title']
    autocomplete_fields = ['city']
    
    def save_model(self, request, obj, form, change):
        """Логирование изменений цен"""
        if change:
            old_obj = DeliveryZone.objects.get(pk=obj.pk)
            old_value = old_obj.delivery_price
        else:
            old_value = None
        
        # Сохраняем объект
        super().save_model(request, obj, form, change)
        
        # Логируем изменение, если цена изменилась
        if change and old_value != obj.delivery_price:
            PriceChangeLog.objects.create(
                entity_type='DELIVERY_ZONE',
                entity_id=obj.pk,
                entity_description=str(obj),
                old_value=old_value,
                new_value=obj.delivery_price,
                changed_by=request.user.email or request.user.username,
            )
        elif not change:
            # Создание новой записи
            PriceChangeLog.objects.create(
                entity_type='DELIVERY_ZONE',
                entity_id=obj.pk,
                entity_description=str(obj),
                old_value=None,
                new_value=obj.delivery_price,
                changed_by=request.user.email or request.user.username,
            )
        
        # Инвалидируем кэш
        pricing_cache.invalidate(f'delivery_zones_{obj.city_id}')


@admin.register(PriceChangeLog)
class PriceChangeLogAdmin(admin.ModelAdmin):
    list_display = ['entity_description', 'old_value', 'new_value', 'changed_at', 'changed_by']
    list_filter = ['entity_type', 'changed_at']
    search_fields = ['entity_description', 'changed_by']
    readonly_fields = [
        'entity_type', 'entity_id', 'entity_description',
        'old_value', 'new_value', 'changed_at', 'changed_by', 'reason'
    ]
    ordering = ['-changed_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

