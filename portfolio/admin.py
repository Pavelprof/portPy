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
    list_display = ('ticker', 'isin', 'issuer', 'type_asset', 'is_tradable', 'created')
    list_display_links = ('ticker',)
    search_fields = ('ticker', 'isin', 'issuer',)
    list_editable = ('is_tradable',)

class DealAdmin(admin.ModelAdmin):
    list_display = ('time_deal', 'in_asset', 'id', 'out_asset')
    list_display_links = ('time_deal', 'in_asset')
    search_fields = ('in_asset',)

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('pk',)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('pk',)

admin.site.register(Deal, DealAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(Account, AccountAdmin)

