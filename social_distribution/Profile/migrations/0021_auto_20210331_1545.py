# Generated by Django 3.1.6 on 2021-03-31 21:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0020_post__host'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='content_type',
            new_name='contentType',
        ),
    ]
