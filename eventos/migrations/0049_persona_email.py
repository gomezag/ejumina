# Generated by Django 4.1.5 on 2023-03-02 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0048_alter_persona_cedula'),
    ]

    operations = [
        migrations.AddField(
            model_name='persona',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]