# Generated by Django 3.2.13 on 2022-06-29 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20220629_2136'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='text',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
