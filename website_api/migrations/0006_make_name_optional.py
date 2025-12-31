# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website_api', '0005_rename_lead_lead_ty_123abc_idx_lead_lead_ty_826d52_idx'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='name',
            field=models.CharField(blank=True, max_length=100, verbose_name='Имя'),
        ),
    ]

