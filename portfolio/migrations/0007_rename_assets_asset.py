# Generated by Django 4.1.7 on 2023-03-28 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0006_rename_assettype_assets_asset_type_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Assets",
            new_name="Asset",
        ),
    ]
