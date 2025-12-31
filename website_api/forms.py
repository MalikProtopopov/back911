"""
Django Admin forms with CKEditor 5 widgets for HTML fields

Все поля, помеченные как (HTML) в verbose_name, используют расширенную конфигурацию CKEditor
с поддержкой стилей, цветов, шрифтов и других возможностей форматирования.
"""
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from website_api.models import CityContent, ServiceContent, Document


class CityContentAdminForm(forms.ModelForm):
    """Форма для редактирования контента города с CKEditor для всех HTML полей"""
    
    # Краткое описание - может содержать простое форматирование
    short_description = forms.CharField(
        widget=CKEditor5Widget(config_name='default'),
        label="Краткое описание",
        help_text="Краткое описание города. Используйте редактор для базового форматирования."
    )
    
    # HTML поля - расширенная конфигурация
    full_description = forms.CharField(
        widget=CKEditor5Widget(config_name='extends'),
        label="Полное описание (HTML)",
        help_text="Подробное описание города и услуг. Используйте редактор для форматирования текста, добавления стилей и цветов."
    )
    advantages_html = forms.CharField(
        widget=CKEditor5Widget(config_name='extends'),
        required=False,
        label="Преимущества (HTML)",
        help_text="HTML блок с преимуществами работы в этом городе. Используйте редактор для форматирования."
    )
    
    class Meta:
        model = CityContent
        fields = '__all__'


class ServiceContentAdminForm(forms.ModelForm):
    """Форма для редактирования контента услуги с CKEditor для всех HTML полей"""
    
    # Краткое описание - базовое форматирование
    short_description = forms.CharField(
        widget=CKEditor5Widget(config_name='default'),
        required=False,
        label="Краткое описание (HTML)",
        help_text="Краткое описание услуги для карточек и превью. Используйте редактор для форматирования."
    )
    
    # Все HTML поля используют расширенную конфигурацию
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='extends'),
        label="Полное описание (HTML)",
        help_text="Полное описание услуги. Используйте редактор для форматирования текста, добавления стилей и цветов."
    )
    how_it_works_html = forms.CharField(
        widget=CKEditor5Widget(config_name='extends'),
        required=False,
        label="Как это работает (HTML)",
        help_text="Пошаговое описание процесса заказа. Используйте редактор для форматирования."
    )
    benefits_html = forms.CharField(
        widget=CKEditor5Widget(config_name='extends'),
        required=False,
        label="Преимущества (HTML)",
        help_text="HTML блок с преимуществами данной услуги. Используйте редактор для форматирования."
    )
    
    class Meta:
        model = ServiceContent
        fields = '__all__'


class DocumentAdminForm(forms.ModelForm):
    """Форма для редактирования документов с CKEditor для HTML полей"""
    
    # Краткое описание - базовое форматирование
    short_description = forms.CharField(
        widget=CKEditor5Widget(config_name='default'),
        required=False,
        label="Краткое описание (HTML)",
        help_text="Краткое описание документа для списков и превью. Используйте редактор для форматирования."
    )
    
    # Полное описание - расширенная конфигурация
    full_description = forms.CharField(
        widget=CKEditor5Widget(config_name='extends'),
        label="Полное описание (HTML)",
        help_text="Полный текст документа. Используйте редактор для форматирования текста, добавления стилей и цветов."
    )
    
    class Meta:
        model = Document
        fields = '__all__'

