from datetime import datetime
from django.db import models
from simple_history.models import HistoricalRecords


class Asset(models.Model):
    BOND = "BD"
    SHARE = "SE"
    REIT = "RT"
    GOOD = "GD"
    CRYPTO = "CO"
    CURRENCY = "CY"
    OTHER = "OR"
    TYPE_ASSET_CHOICES = [
        (BOND, "Bond"),
        (SHARE, "Share"),
        (REIT, "Reit"),
        (GOOD, "Good"),
        (CRYPTO, "Crypto"),
        (CURRENCY, "Currency"),
        (OTHER, "Other"),]
    ticker = models.CharField(max_length=20)
    isin = models.CharField(max_length=100, unique=True)
    name_asset = models.CharField(max_length=100)
    issuer = models.CharField(max_length=100)
    icon = models.ImageField(upload_to="icons/", null=True)
    currency_influence = models.ForeignKey('Asset', related_name='+', on_delete=models.PROTECT)
    country = models.CharField(max_length=50)
    type_asset = models.CharField(max_length=2, choices=TYPE_ASSET_CHOICES, default=OTHER)
    is_tradable = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ticker

class Deal(models.Model):
    class Exchanges(models.IntegerChoices):
        MOEX = 1
        SPB = 2
        Binance = 3
        NYSE = 4
    account = models.ForeignKey('Account', on_delete=models.PROTECT)
    out_asset = models.ForeignKey('Asset', related_name='out_asset', on_delete=models.PROTECT)
    in_asset = models.ForeignKey('Asset', related_name='in_asset', on_delete=models.PROTECT)
    out_quantity = models.FloatField()
    in_quantity = models.IntegerField()
    lot_exchange_rate = models.FloatField()
    exchange = models.IntegerField(choices=Exchanges.choices, default=1)
    note = models.TextField(max_length=10000, null=True)
    time_deal = models.DateTimeField(default=datetime.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(cascade_delete_history=True)

    def __str__(self):
        return str(self.pk)

    class Meta:
        ordering = ['time_deal']

class Transaction(models.Model):
    account = models.ForeignKey('Account', on_delete=models.PROTECT)
    deal = models.ForeignKey('Deal', on_delete=models.SET_NULL, null=True)
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True)
    asset_transaction = models.ForeignKey('Asset', on_delete=models.PROTECT)
    quantity_transaction = models.FloatField()
    type_transaction = models.CharField(max_length=50)
    time_transaction = models.DateTimeField(default=datetime.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pk)

    class Meta:
        ordering = ['time_transaction']

class Portfolio(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    name_portfolio = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_portfolio

class Account(models.Model):
    portfolio = models.ForeignKey('Portfolio', on_delete=models.SET_NULL, null=True)
    name_account = models.CharField(max_length=50)
    broker = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_account

class Position(models.Model):
    asset = models.ForeignKey('Asset', on_delete=models.PROTECT)
    account = models.ForeignKey('Account', on_delete=models.PROTECT)
    quantity_position = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pk)
