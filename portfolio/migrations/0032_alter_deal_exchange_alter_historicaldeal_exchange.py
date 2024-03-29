# Generated by Django 4.1.7 on 2023-05-02 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0031_alter_asset_type_asset"),
    ]

    operations = [
        migrations.AlterField(
            model_name="deal",
            name="exchange",
            field=models.IntegerField(
                choices=[(1, "Moex"), (2, "Spb"), (3, "Binance"), (4, "Nyse")],
                default=1,
            ),
        ),
        migrations.AlterField(
            model_name="historicaldeal",
            name="exchange",
            field=models.IntegerField(
                choices=[(1, "Moex"), (2, "Spb"), (3, "Binance"), (4, "Nyse")],
                default=1,
            ),
        ),
    ]
