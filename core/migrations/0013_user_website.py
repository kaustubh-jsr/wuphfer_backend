# Generated by Django 3.2.13 on 2022-07-26 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_bookmark_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='website',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
