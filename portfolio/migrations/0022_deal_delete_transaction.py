# Generated by Django 4.1.7 on 2023-04-24 19:35

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0021_remove_transaction_fee_remove_transaction_tax_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Deal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField()),
                ("exchange", models.CharField(max_length=255)),
                ("lot_price", models.FloatField()),
                ("paid", models.FloatField()),
                ("payment_currency", models.CharField(max_length=255)),
                (
                    "time_deal",
                    models.DateTimeField(
                        default=datetime.datetime(2023, 4, 24, 22, 35, 36, 865768)
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "asset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="portfolio.asset",
                    ),
                ),
            ],
            options={
                "ordering": ["time_deal"],
            },
        ),
        migrations.DeleteModel(
            name="Transaction",
        ),
    ]
