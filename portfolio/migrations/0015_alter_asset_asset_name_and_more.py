# Generated by Django 4.1.7 on 2023-04-21 06:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0014_asset_asset_name_alter_transaction_time_transaction"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asset",
            name="asset_name",
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="transaction",
            name="time_transaction",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 4, 21, 9, 47, 1, 767563)
            ),
        ),
    ]
