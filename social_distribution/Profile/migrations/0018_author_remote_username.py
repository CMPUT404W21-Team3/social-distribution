# Generated by Django 3.1.6 on 2021-03-31 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0017_remove_author_displayname'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='remote_username',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
