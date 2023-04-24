from django.contrib import admin
from .models import *

from import_export.admin import ImportExportActionModelAdmin
from import_export import resources
from import_export import fields
from import_export.widgets import ForeignKeyWidget

class AssetResource(resources.ModelResource):

    class Meta:
        model = Asset
        exclude = ['id']
        import_id_fields = ['isin']
class AssetAdmin(ImportExportActionModelAdmin):
    resource_class = AssetResource
    list_display = ('ticker', 'isin', 'issuer', 'asset_type', 'is_tradable', 'created')
    list_display_links = ('ticker',)
    search_fields = ('ticker', 'isin', 'issuer',)
    list_editable = ('is_tradable',)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('time_transaction', 'asset', 'id', 'payment_currency')
    list_display_links = ('time_transaction', 'asset')
    search_fields = ('asset',)

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Asset, AssetAdmin)