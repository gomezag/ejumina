# Generated by Django 4.1.5 on 2023-03-02 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0049_persona_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitacion',
            name='estado',
            field=models.CharField(choices=[('ACT', 'Activa'), ('RES', 'Reservada'), ('USA', 'Usada'), ('CAN', 'Cancelada')], default='ACT', max_length=3),
        ),
    ]
