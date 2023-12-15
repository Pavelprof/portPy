from django.contrib import admin
from .models import *

from import_export.admin import ImportExportActionModelAdmin
from import_export import resources
from import_export import fields
from import_export.widgets import ForeignKeyWidget

class AssetResource(resources.ModelResource):
    class Meta:
        model = Asset
        exclude = ['created', 'updated']
        import_id_fields = ['ticker']

class AssetAdmin(ImportExportActionModelAdmin):
    resource_class = AssetResource
    list_display = ('id', 'ticker', 'figi', 'isin', 'full_name_asset', 'type_asset', 'is_tradable', 'created')
    list_display_links = ('id', 'ticker',)
    search_fields = ('ticker', 'isin', 'full_name_asset', 'name_asset', 'figi')
    list_editable = ('is_tradable',)

class TransactionAdmin(ImportExportActionModelAdmin):
    list_display = ('id', 'type_transaction', 'quantity_transaction', 'asset_transaction', 'account', "exchange")
    list_display_links = ('id', 'type_transaction')
    search_fields = ('type_transaction', 'asset_transaction__ticker__icontains')

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('pk',)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name_account', 'broker', 'country_account')
    list_display_links = ('pk', 'name_account',)

class AssetGroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'creator', 'created')
    list_display_links = ('pk', 'name')
    search_fields = ('name', 'description')

class StructureAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'owner', 'created')
    list_display_links = ('pk', 'name')
    search_fields = ('name',)

class TargetWeightAdmin(admin.ModelAdmin):
    list_display = ('pk', 'target_weight', 'structure', 'asset_group', 'created', 'updated')
    list_display_links = ('pk', 'target_weight',)
    search_fields = ('structure', 'asset_group',)

class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'mic', 'name', 'created')
    list_display_links = ('pk', 'mic', 'name')


admin.site.register(Exchange, ExchangeAdmin)
admin.site.register(TargetWeight, TargetWeightAdmin)
admin.site.register(Structure, StructureAdmin)
admin.site.register(AssetGroup, AssetGroupAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(Account, AccountAdmin)

