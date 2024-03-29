# Generated by Django 4.1.7 on 2023-03-28 14:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0007_rename_assets_asset"),
    ]

    operations = [
        migrations.RenameField(
            model_name="asset",
            old_name="currency",
            new_name="payment_currency",
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
                ("name", models.CharField(max_length=255)),
                ("quantity", models.IntegerField()),
                ("broker", models.CharField(max_length=255)),
                ("exchange", models.CharField(max_length=255)),
                ("lot_price", models.FloatField()),
                ("paid", models.FloatField()),
                ("fee", models.FloatField()),
                ("tax", models.FloatField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("payment_currency", models.IntegerField()),
                (
                    "asset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="portfolio.asset",
                    ),
                ),
            ],
        ),
    ]
