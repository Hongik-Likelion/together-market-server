# Generated by Django 4.2.4 on 2023-08-15 05:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0002_board_purchased_products_alter_board_rating'),
    ]

    operations = [
        migrations.RenameField(
            model_name='board',
            old_name='market',
            new_name='market_id',
        ),
        migrations.RenameField(
            model_name='board',
            old_name='shop',
            new_name='shop_id',
        ),
        migrations.RenameField(
            model_name='board',
            old_name='user',
            new_name='user_id',
        ),
    ]
