# Generated by Django 4.1.7 on 2023-04-28 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0030_deal_account_historicaldeal_account"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asset",
            name="type_asset",
            field=models.CharField(
                choices=[
                    ("BD", "Bond"),
                    ("SE", "Share"),
                    ("RT", "Reit"),
                    ("GD", "Good"),
                    ("CO", "Crypto"),
                    ("CY", "Currency"),
                    ("OR", "Other"),
                ],
                default="OR",
                max_length=2,
            ),
        ),
    ]