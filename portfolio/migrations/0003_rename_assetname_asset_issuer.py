# Generated by Django 4.1.7 on 2023-03-05 06:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0002_rename_istradeble_asset_istradable"),
    ]

    operations = [
        migrations.RenameField(
            model_name="asset",
            old_name="assetName",
            new_name="issuer",
        ),
    ]