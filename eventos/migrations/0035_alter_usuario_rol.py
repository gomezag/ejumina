# Generated by Django 4.1.5 on 2023-02-19 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0034_alter_listainvitados_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='rol',
            field=models.IntegerField(choices=[(0, 'Admin'), (1, 'Bouncer'), (2, 'R.R.P.P.'), (3, 'Guest')]),
        ),
    ]