# Generated by Django 4.1.7 on 2023-04-25 06:38

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portfolio", "0022_deal_delete_transaction"),
    ]

    operations = [
        migrations.AlterField(
            model_name="deal",
            name="time_deal",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 4, 25, 9, 38, 24, 654600)
            ),
        ),
        migrations.CreateModel(
            name="HistoricalDeal",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
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
                        default=datetime.datetime(2023, 4, 25, 9, 38, 24, 654600)
                    ),
                ),
                ("created", models.DateTimeField(blank=True, editable=False)),
                ("updated", models.DateTimeField(blank=True, editable=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "asset",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="portfolio.asset",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical deal",
                "verbose_name_plural": "historical deals",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]