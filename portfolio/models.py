from django.core.exceptions import ValidationError
from django.db import models
from simple_history.models import HistoricalRecords
from django.utils import timezone
from django_countries.fields import CountryField

class Asset(models.Model):
    BOND = "BD"
    SHARE = "SE"
    REIT = "RT"
    GOOD = "GD"
    CRYPTO = "CO"
    CURRENCY = "CY"
    ETF = "ET"
    OTHER = "OR"
    TYPE_ASSET_CHOICES = [
        (BOND, "Bond"),
        (SHARE, "Share"),
        (REIT, "Reit"),
        (GOOD, "Good"),
        (CRYPTO, "Crypto"),
        (CURRENCY, "Currency"),
        (ETF, "Etf"),
        (OTHER, "Other"),]

    class Exchanges(models.IntegerChoices):
        MOEX = 1
        SPB = 2
        Binance = 3
        NYSE = 4

    ticker = models.CharField(max_length=20, unique=True)
    isin = models.CharField(max_length=12, unique=True, null=True, blank=True)
    figi = models.CharField(max_length=12, unique=True, null=True, blank=True)
    name_asset = models.CharField(max_length=100, null=True, blank=True)
    full_name_asset = models.CharField(max_length=200)
    icon = models.ImageField(upload_to="icons/", null=True, blank=True)
    currency_influence = models.ForeignKey('Asset', related_name='+', on_delete=models.PROTECT, null=True, blank=True)
    currency_base_settlement = models.ForeignKey('Asset', related_name='+', on_delete=models.PROTECT)
    country_asset = CountryField(null=True, blank=True, default='US')
    type_asset = models.CharField(max_length=2, choices=TYPE_ASSET_CHOICES, default=OTHER)
    type_base_asset = models.CharField(max_length=2, choices=TYPE_ASSET_CHOICES, default=OTHER)
    exchange = models.IntegerField(choices=Exchanges.choices, default=1)
    class_code = models.CharField(max_length=20, null=True, blank=True)
    note = models.CharField(max_length=5000, null=True, blank=True)
    is_tradable = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ticker


class Transaction(models.Model):
    class Types_transaction(models.IntegerChoices):
        BUY = 1
        SELL = 2
        FUND = 3
        PROFIT = 4
        FEE = 5
        TAX = 6
        WITHDRAWAL = 7
    account = models.ForeignKey('Account', on_delete=models.PROTECT)
    related_transaction = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, blank=True)
    asset_transaction = models.ForeignKey('Asset', on_delete=models.PROTECT)
    quantity_transaction = models.FloatField()
    type_transaction = models.IntegerField(choices=Types_transaction.choices, default=1)
    note = models.TextField(max_length=10000, null=True, blank=True)
    time_transaction = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(cascade_delete_history=True)

    def clean(self):
        super().clean()
        if self.type_transaction in [self.Types_transaction.FUND, self.Types_transaction.BUY,
                                     self.Types_transaction.PROFIT] and type(self.quantity_transaction) in (int, float) and self.quantity_transaction < 0:
            raise ValidationError(
                {'quantity_transaction' : ["For 'FUND', 'BUY' and 'PROFIT' transactions, quantity_transaction should be positive.",]})
        elif self.type_transaction in [self.Types_transaction.SELL, self.Types_transaction.FEE, self.Types_transaction.TAX,
                                       self.Types_transaction.WITHDRAWAL] and type(self.quantity_transaction) in (int, float) and self.quantity_transaction > 0:
            raise ValidationError(
                {'quantity_transaction' : ["For 'SELL' 'FEE', 'TAX', and 'WITHDRAWAL' transactions, quantity_transaction should be negative.",]})

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
    portfolio = models.ForeignKey('Portfolio', on_delete=models.SET_NULL, null=True, blank=True)
    name_account = models.CharField(max_length=50)
    country_account = CountryField(null=True, blank=True, default='US')
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