# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website_api', '0003_update_technic_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='lead_type',
            field=models.CharField(
                choices=[
                    ('service', 'Заявка по услуге от клиента'),
                    ('feedback', 'Заявка с предложениями или обратной связью'),
                    ('partnership', 'Заявка на партнерство'),
                ],
                default='service',
                max_length=20,
                verbose_name='Тип заявки'
            ),
        ),
        migrations.AddField(
            model_name='lead',
            name='page_url',
            field=models.URLField(
                blank=True,
                max_length=500,
                verbose_name='URL страницы с которой создана заявка'
            ),
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['lead_type', '-created_at'], name='lead_lead_ty_123abc_idx'),
        ),
    ]

