# Generated by Django 2.0.6 on 2018-06-18 12:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yellowant_api', '0005_auto_20180615_0715'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='box_credentials',
            name='BOX_CLIENT_ID',
        ),
        migrations.RemoveField(
            model_name='box_credentials',
            name='BOX_CLIENT_SECRET',
        ),
    ]
