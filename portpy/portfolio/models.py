from django.db import models

class Asset(models.Model):
    ticker = models.CharField(max_length=255)
    description = models.TextField()
    isin = models.CharField(max_length=255)
    assetName = models.CharField(max_length=255)
    icon =
    currency = models.CharField(max_length=255)
    settlementCurrency = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    assetType = models.CharField(max_length=255)
    isTradeble = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField
