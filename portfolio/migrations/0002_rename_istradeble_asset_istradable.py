# Generated by Django 4.1.7 on 2023-03-05 05:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="asset",
            old_name="isTradeble",
            new_name="isTradable",
        ),
    ]