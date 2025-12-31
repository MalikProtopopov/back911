# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website_api', '0006_make_name_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicecontent',
            name='short_description',
            field=models.TextField(
                blank=True,
                default='',
                verbose_name='Краткое описание (HTML)',
                help_text='Краткое описание услуги для карточек и превью'
            ),
            preserve_default=False,
        ),
    ]

