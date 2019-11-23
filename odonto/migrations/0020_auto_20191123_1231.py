# Generated by Django 2.2.4 on 2019-11-23 12:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('odonto', '0019_email_telefono'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paciente',
            name='obras_sociales',
        ),
        migrations.AddField(
            model_name='norma_trabajo',
            name='bonos',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='norma_trabajo',
            name='coseguro',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='obra_social',
            name='usa_autorizacion',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='obra_social',
            name='usa_bonos',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='obra_social',
            name='usa_coseguro',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='obra_social',
            name='usa_planes',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='norma_trabajo',
            name='años',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='norma_trabajo',
            name='dias',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='norma_trabajo',
            name='meses',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('obra_social', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='odonto.Obra_Social')),
            ],
        ),
        migrations.CreateModel(
            name='PacienteObraSocial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nro_afiliado', models.CharField(max_length=20, verbose_name='Nro. Afiliado')),
                ('obra_social', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='odonto.Obra_Social')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='odonto.Paciente')),
                ('plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='odonto.Plan')),
            ],
        ),
    ]
