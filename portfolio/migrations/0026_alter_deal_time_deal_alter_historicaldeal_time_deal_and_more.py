# Generated by Django 4.1.7 on 2023-04-26 16:23

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portfolio", "0025_alter_deal_note_alter_deal_time_deal_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="deal",
            name="time_deal",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 4, 26, 19, 23, 56, 722327)
            ),
        ),
        migrations.AlterField(
            model_name="historicaldeal",
            name="time_deal",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 4, 26, 19, 23, 56, 722327)
            ),
        ),
        migrations.CreateModel(
            name="Portfolio",
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
                ("portfolio_name", models.CharField(max_length=50)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
