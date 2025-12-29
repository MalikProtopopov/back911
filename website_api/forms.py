"""
Django Admin forms with CKEditor 5 widgets for HTML fields
"""
from django import forms
# Temporarily disabled due to installation issues
# from django_ckeditor_5.widgets import CKEditor5Widget
from website_api.models import CityContent, ServiceContent


class CityContentAdminForm(forms.ModelForm):
    """Форма для редактирования контента города с CKEditor"""
    
    full_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10}),  # Temporarily using Textarea
        # widget=CKEditor5Widget(config_name='extends'),
        label="Полное описание (HTML)",
        help_text="Подробное описание города и услуг"
    )
    advantages_html = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),  # Temporarily using Textarea
        # widget=CKEditor5Widget(config_name='default'),
        required=False,
        label="Преимущества (HTML)",
        help_text="HTML блок с преимуществами работы в этом городе"
    )
    
    class Meta:
        model = CityContent
        fields = '__all__'


class ServiceContentAdminForm(forms.ModelForm):
    """Форма для редактирования контента услуги с CKEditor"""
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10}),  # Temporarily using Textarea
        # widget=CKEditor5Widget(config_name='extends'),
        label="Описание (HTML)",
        help_text="Полное описание услуги"
    )
    how_it_works_html = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),  # Temporarily using Textarea
        # widget=CKEditor5Widget(config_name='default'),
        required=False,
        label="Как это работает (HTML)",
        help_text="Пошаговое описание процесса заказа"
    )
    benefits_html = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),  # Temporarily using Textarea
        # widget=CKEditor5Widget(config_name='default'),
        required=False,
        label="Преимущества (HTML)",
        help_text="HTML блок с преимуществами данной услуги"
    )
    
    class Meta:
        model = ServiceContent
        fields = '__all__'

