# Generated by Django 4.1.7 on 2023-03-27 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0004_rename_asset_assets"),
    ]

    operations = [
        migrations.RenameField(
            model_name="assets",
            old_name="settlementCurrency",
            new_name="settlement_currency",
        ),
    ]
