# Generated by Django 3.1.6 on 2021-04-13 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0036_post_to_remote_author_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='remote_url',
            field=models.CharField(default='http://localhost:8000/', max_length=300, null=True),
        ),
    ]