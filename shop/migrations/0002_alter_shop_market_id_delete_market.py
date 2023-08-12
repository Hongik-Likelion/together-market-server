# Generated by Django 4.2.4 on 2023-08-11 08:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0001_initial'),
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='market_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.market'),
        ),
        migrations.DeleteModel(
            name='Market',
        ),
    ]
