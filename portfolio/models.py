from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import JSONField
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
        OUT = 0 # It's for not pared currencies (USD, RUB, EUR...). Because they can have the same ticker as any asset at any axchange
        MOEX = 1
        SPB = 2
        Binance = 3
        NYSE = 4

    ticker = models.CharField(max_length=20) # unique within one exchange ...clean()
    isin = models.CharField(max_length=12, unique=True, null=True, blank=True)
    figi = models.CharField(max_length=12, unique=True, null=True, blank=True)
    name_asset = models.CharField(max_length=100, null=True, blank=True)
    full_name_asset = models.CharField(max_length=200)
    icon = models.ImageField(upload_to="icons/", null=True, blank=True)
    currency_influence = models.ForeignKey('Asset', related_name='+', on_delete=models.PROTECT, null=True, blank=True) # For bonds it's also a nominal currency
    currency_base_settlement = models.ForeignKey('Asset', related_name='+', on_delete=models.PROTECT)
    country_asset = CountryField(null=True, blank=True, default='US')
    type_asset = models.CharField(max_length=2, choices=TYPE_ASSET_CHOICES, default=OTHER)
    type_base_asset = models.CharField(max_length=2, choices=TYPE_ASSET_CHOICES, default=OTHER)
    exchange = models.IntegerField(choices=Exchanges.choices, default=1)
    class_code = models.CharField(max_length=20, null=True, blank=True)
    bond_nominal = models.DecimalField(max_digits=40, decimal_places=15, null=True, blank=True)
    note = models.CharField(max_length=5000, null=True, blank=True)
    is_tradable = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        existing_assets = self.__class__.objects.filter(ticker=self.ticker, exchange=self.exchange)
        if self.pk:
            existing_assets = existing_assets.exclude(pk=self.pk)
        if existing_assets.exists():
            raise ValidationError(
                {
                    "ticker": "The ticker must be unique within one exchange"
                }
            )

        if self.type_asset == self.BOND and self.bond_nominal is None:
            raise ValidationError({
                'bond_nominal': 'Bond nominal cannot be null for assets of type Bond.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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

class AssetGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    creator = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    filters = JSONField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Structure(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class TargetWeight(models.Model):
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE)
    asset_group = models.ForeignKey(AssetGroup, on_delete=models.CASCADE)
    target_value = models.DecimalField(max_digits=5, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.structure.name} - {self.target_value}%"