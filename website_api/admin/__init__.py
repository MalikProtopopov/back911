from django.contrib import admin
from website_api.models import (
    City, Service, TechnicCategory, Option, OptionPrice,
    CityContent, ServiceContent, Advantage, Metric,
    Contact, AppLink, SeoMeta, Lead
)
from website_api.forms import CityContentAdminForm, ServiceContentAdminForm


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


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CityContentInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(TechnicCategory)
class TechnicCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'service']
    list_filter = ['service']


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ['title', 'service', 'is_active']
    list_filter = ['service', 'is_active']
    search_fields = ['title']


@admin.register(OptionPrice)
class OptionPriceAdmin(admin.ModelAdmin):
    list_display = ['option', 'city', 'technic_category', 'amount']
    list_filter = ['city', 'option__service']
    search_fields = ['option__title', 'city__title']


@admin.register(ServiceContent)
class ServiceContentAdmin(admin.ModelAdmin):
    form = ServiceContentAdminForm
    list_display = ['service', 'city', 'updated_at']
    list_filter = ['service', 'city']
    search_fields = ['service__title', 'city__title', 'meta_title']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('service', 'city'),
            'description': 'Если город не выбран - контент будет общим для всех городов'
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'h1_title')
        }),
        ('Контент (HTML)', {
            'fields': ('description', 'how_it_works_html', 'benefits_html'),
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


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'city', 'service', 'status', 'created_at']
    list_filter = ['status', 'city', 'service', 'created_at']
    search_fields = ['name', 'phone', 'email']
    readonly_fields = ['created_at']
    
    actions = ['mark_as_processing']
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_as_processing.short_description = "Отметить как обработано"

