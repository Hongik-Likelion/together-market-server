# Generated by Django 4.2.4 on 2023-08-12 17:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_blacklist'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blacklist',
            old_name='user_id',
            new_name='user',
        ),
    ]
