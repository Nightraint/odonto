# Generated by Django 2.2.4 on 2019-10-12 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('odonto', '0010_auto_20191010_0230'),
    ]

    operations = [
        migrations.AddField(
            model_name='odontologo',
            name='obras_sociales',
            field=models.ManyToManyField(blank=True, to='odonto.Obra_Social'),
        ),
    ]
