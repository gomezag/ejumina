# Generated by Django 4.1.7 on 2024-06-02 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0001_initial_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
    ]