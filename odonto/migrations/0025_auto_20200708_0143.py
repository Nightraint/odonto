# Generated by Django 2.2.4 on 2020-07-08 04:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('odonto', '0024_cuenta_corriente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cuenta_corriente',
            name='paciente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='odonto.Paciente'),
        ),
    ]