# Generated by Django 2.2.4 on 2020-01-21 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('odonto', '0006_auto_20200121_0058'),
    ]

    operations = [
        migrations.AddField(
            model_name='ficha',
            name='nro_afiliado',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
