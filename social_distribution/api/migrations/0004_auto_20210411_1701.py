# Generated by Django 3.1.6 on 2021-04-11 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20210410_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='incoming_password',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='connection',
            name='incoming_username',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='connection',
            name='name',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='connection',
            name='outgoing_password',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='connection',
            name='outgoing_username',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='connection',
            name='url',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]