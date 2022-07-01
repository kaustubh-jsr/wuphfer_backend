# Generated by Django 3.2.13 on 2022-06-30 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_notification_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='seen',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(blank=True, choices=[('like', 'like'), ('comment', 'comment'), ('rewuphf', 'rewuphf'), ('follow', 'follow')], max_length=32, null=True),
        ),
    ]
