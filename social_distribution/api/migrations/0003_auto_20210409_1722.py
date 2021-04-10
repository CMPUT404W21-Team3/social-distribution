# Generated by Django 3.1.6 on 2021-04-09 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20210323_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='connection',
            name='incoming_username',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='connection',
            name='outgoing_password',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='connection',
            name='outgoing_username',
            field=models.CharField(max_length=20, null=True),
        ),
    ]