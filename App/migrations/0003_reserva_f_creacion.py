# Generated by Django 5.0.2 on 2024-11-19 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0002_rename_cantidadpersonas_reserva_cantidadhermanos_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reserva',
            name='F_Creacion',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
