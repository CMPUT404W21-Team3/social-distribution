# Generated by Django 3.1.6 on 2021-03-31 08:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0016_author_displayname'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='author',
            name='displayName',
        ),
    ]