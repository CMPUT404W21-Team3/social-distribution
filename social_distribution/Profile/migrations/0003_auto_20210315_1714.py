# Generated by Django 3.1.7 on 2021-03-15 23:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0002_auto_20210305_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='to_author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_author', to='Profile.author'),
        ),
        migrations.AlterField(
            model_name='post',
            name='visibility',
            field=models.CharField(choices=[('PUBLIC', 'Public'), ('FRIENDS', 'Friends'), ('PRIVATE', 'Private')], default='PUBLIC', max_length=10),
        ),
    ]