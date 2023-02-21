# Generated by Django 4.1.5 on 2023-02-21 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0041_evento_fecha'),
    ]

    operations = [
        migrations.AddField(
            model_name='listainvitados',
            name='personas_free',
            field=models.ManyToManyField(blank=True, related_name='invitados_free', through='eventos.Free', to='eventos.persona'),
        ),
        migrations.AlterField(
            model_name='listainvitados',
            name='personas',
            field=models.ManyToManyField(blank=True, related_name='invitados', through='eventos.Invitacion', to='eventos.persona'),
        ),
    ]