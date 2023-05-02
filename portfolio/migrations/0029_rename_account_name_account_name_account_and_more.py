# Generated by Django 4.1.7 on 2023-04-27 14:39

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0028_position"),
    ]

    operations = [
        migrations.RenameField(
            model_name="account",
            old_name="account_name",
            new_name="name_account",
        ),
        migrations.RenameField(
            model_name="asset",
            old_name="asset_name",
            new_name="name_asset",
        ),
        migrations.RenameField(
            model_name="asset",
            old_name="asset_type",
            new_name="type_asset",
        ),
        migrations.RenameField(
            model_name="portfolio",
            old_name="portfolio_name",
            new_name="name_portfolio",
        ),
        migrations.RenameField(
            model_name="position",
            old_name="quantity",
            new_name="quantity_position",
        ),
        migrations.CreateModel(
            name="Transaction",
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
                ("quantity_transaction", models.FloatField()),
                ("type_transaction", models.CharField(max_length=50)),
                (
                    "time_transaction",
                    models.DateTimeField(default=datetime.datetime.now),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="portfolio.account",
                    ),
                ),
                (
                    "asset_transaction",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="portfolio.asset",
                    ),
                ),
                (
                    "deal",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="portfolio.deal",
                    ),
                ),
                (
                    "position",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="portfolio.position",
                    ),
                ),
            ],
            options={
                "ordering": ["time_transaction"],
            },
        ),
    ]
