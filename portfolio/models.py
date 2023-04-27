from datetime import datetime
from django.db import models
from simple_history.models import HistoricalRecords


class Asset(models.Model):
    ticker = models.CharField(max_length=20)
    isin = models.CharField(max_length=50, unique=True)
    asset_name = models.CharField(max_length=50)
    issuer = models.CharField(max_length=100)
    icon = models.ImageField(upload_to="icons/", null=True)
    currency_influence = models.ForeignKey('Asset', related_name='+', on_delete=models.PROTECT)
    country = models.CharField(max_length=50)
    asset_type = models.CharField(max_length=50)
    is_tradable = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.ticker

class Deal(models.Model):
    out_asset = models.ForeignKey('Asset', related_name='out_asset', on_delete=models.PROTECT)
    in_asset = models.ForeignKey('Asset', related_name='in_asset', on_delete=models.PROTECT)
    out_quantity = models.FloatField()
    in_quantity = models.IntegerField()
    lot_exchange_rate = models.FloatField()
    exchange = models.CharField(max_length=50)
    note = models.TextField(max_length=10000, null=True)
    time_deal = models.DateTimeField(default=datetime.now())
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.pk)

    class Meta:
        ordering = ['time_deal']

class Portfolio(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    portfolio_name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.portfolio_name

class Account(models.Model):
    portfolio = models.ForeignKey('Portfolio', on_delete=models.SET_NULL, null=True)
    account_name = models.CharField(max_length=50)
    broker = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.account_name