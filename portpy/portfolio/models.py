from datetime import datetime

from django.db import models

class Asset(models.Model):
    ticker = models.CharField(max_length=255)
    isin = models.CharField(max_length=255, unique=True)
    asset_name = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    icon = models.ImageField(upload_to="icons/", null=True)
    payment_currency = models.CharField(max_length=255)
    settlement_currency = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=255)
    is_tradable = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.ticker

class Transaction(models.Model):
    quantity = models.IntegerField()
    exchange = models.CharField(max_length=255)
    lot_price = models.FloatField()
    paid = models.FloatField()
    fee = models.FloatField(null=True)
    tax = models.FloatField(null=True)
    payment_currency = models.CharField(max_length=255)
    time_transaction = models.DateTimeField(default=datetime.now())
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    asset = models.ForeignKey('Asset', on_delete=models.PROTECT)

    def __str__(self):
        return self.exchange

    class Meta:
        ordering = ['time_transaction']