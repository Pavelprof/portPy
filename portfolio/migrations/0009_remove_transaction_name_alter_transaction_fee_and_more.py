# Generated by Django 4.1.7 on 2023-03-28 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0008_rename_currency_asset_payment_currency_transaction"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transaction",
            name="name",
        ),
        migrations.AlterField(
            model_name="transaction",
            name="fee",
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="tax",
            field=models.FloatField(null=True),
        ),
    ]
