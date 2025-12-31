# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website_api', '0004_add_lead_type_and_page_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='name',
            field=models.CharField(blank=True, max_length=100, verbose_name='Имя'),
        ),
    ]

