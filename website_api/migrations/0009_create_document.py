# Generated manually for Document model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website_api', '0008_rename_lead_lead_ty_123abc_idx_lead_lead_ty_826d52_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название документа')),
                ('slug', models.SlugField(
                    max_length=255,
                    unique=True,
                    verbose_name='URL slug',
                    help_text='Уникальный идентификатор для URL (генерируется автоматически из названия)'
                )),
                ('version', models.CharField(
                    default='1.0',
                    max_length=20,
                    verbose_name='Версия документа',
                    help_text='Версия документа, например: 1.0, 2.1, v1.2.3'
                )),
                ('is_active', models.BooleanField(
                    default=True,
                    verbose_name='Активен',
                    help_text='Неактивные документы не отображаются на сайте'
                )),
                ('short_description', models.TextField(
                    blank=True,
                    verbose_name='Краткое описание (HTML)',
                    help_text='Краткое описание документа для превью и списков'
                )),
                ('full_description', models.TextField(
                    verbose_name='Полное описание (HTML)',
                    help_text='Полный текст документа'
                )),
                ('meta_title', models.CharField(
                    max_length=255,
                    verbose_name='SEO Title',
                    help_text='Заголовок страницы для поисковых систем'
                )),
                ('meta_description', models.TextField(
                    verbose_name='SEO Meta Description',
                    help_text='Описание страницы для поисковых систем'
                )),
                ('meta_keywords', models.TextField(
                    blank=True,
                    verbose_name='SEO Meta Keywords',
                    help_text='Ключевые слова для поисковых систем (опционально)'
                )),
                ('h1_title', models.CharField(
                    max_length=255,
                    verbose_name='H1 заголовок',
                    help_text='Основной заголовок на странице документа'
                )),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Дата создания'
                )),
                ('updated_at', models.DateTimeField(
                    auto_now=True,
                    verbose_name='Дата обновления'
                )),
            ],
            options={
                'db_table': 'document',
                'verbose_name': 'Документ',
                'verbose_name_plural': 'Документы',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['slug'], name='document_slug_idx'),
        ),
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['is_active'], name='document_active_idx'),
        ),
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['is_active', '-updated_at'], name='document_active_updated_idx'),
        ),
    ]

