from rest_framework import serializers
from .models import Deal, Position, Asset, Transaction
from .api_services import *

class AssetSerializer(serializers.ModelSerializer):
    type_asset_display = serializers.CharField(source='get_type_asset_display', read_only=True)
    price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    currency_base_settlement = serializers.CharField(source='currency_base_settlement.ticker')

    class Meta:
        model = Asset
        fields = ('id', 'ticker', 'isin', 'figi', 'name_asset', 'full_name_asset', 'price', 'currency', 'currency_base_settlement', 'type_asset',
                  'type_asset_display', 'is_tradable', 'currency_influence', 'created')

    def get_price(self, obj):
        prices_and_currencies = self.context.get('prices_and_currencies', {})
        return prices_and_currencies.get(obj.id, {}).get('price', None)

    def get_currency(self, obj):
        prices_and_currencies = self.context.get('prices_and_currencies', {})
        asset_currency = prices_and_currencies.get(obj.id, {}).get('currency', None)
        return asset_currency.ticker


class PositionSerializer(serializers.ModelSerializer):
    asset = AssetSerializer()
    total_value = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ('asset', 'account', 'quantity_position', 'total_value')

    def get_total_value(self, obj):
        prices_and_currencies = self.context.get('prices_and_currencies', {})
        settlement_currency = self.context.get('settlement_currency')
        price_asset = prices_and_currencies.get(obj.asset.id, {}).get('price', 0)
        currency_asset = prices_and_currencies.get(obj.asset.id, {}).get('currency', None)

        if currency_asset == settlement_currency:
            return price_asset * obj.quantity_position

        for asset, asset_info in prices_and_currencies.items():
            currency = asset_info.get('currency')
            currency_influence = asset_info.get('currency_influence')
            type_asset = asset_info.get('type_asset')

            if currency == settlement_currency and currency_influence == obj.asset.currency_base_settlement and type_asset == "CY":
                exchange_rate_asset = asset_info.get('price')
                break

        return price_asset * obj.quantity_position * exchange_rate_asset




class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('account', 'deal', 'position', 'asset_transaction', 'quantity_transaction',
                  'type_transaction', 'time_transaction', 'created', 'updated')


class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ('account', 'out_asset', 'out_quantity', 'in_asset', 'in_quantity',
                  'exchange', 'note', 'time_deal', 'created', 'updated')