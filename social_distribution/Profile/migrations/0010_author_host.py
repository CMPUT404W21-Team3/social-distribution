# Generated by Django 3.1.6 on 2021-03-25 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0009_merge_20210324_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='host',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
