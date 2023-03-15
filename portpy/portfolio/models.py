from django.db import models

class Assets(models.Model):
    ticker = models.CharField(max_length=255)
    description = models.TextField()
    isin = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    icon = models.ImageField(upload_to="icons/")
    currency = models.CharField(max_length=255)
    settlementCurrency = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    assetType = models.CharField(max_length=255)
    isTradable = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.ticker