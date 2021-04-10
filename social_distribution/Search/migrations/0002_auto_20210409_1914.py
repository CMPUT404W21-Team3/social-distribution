# Generated by Django 3.2 on 2021-04-10 01:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0002_auto_20210409_1914'),
        ('Search', '0005_friendrequest_remote_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendrequest',
            name='remote_sender',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='friendrequest',
            name='remote_username',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='friendrequest',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='Profile.author'),
        ),
    ]
