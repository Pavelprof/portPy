from rest_framework import serializers
from .models import Deal, Position, Asset, Transaction
from .api_services import *


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


class AssetSerializer(serializers.ModelSerializer):
    type_asset_display = serializers.CharField(source='get_type_asset_display', read_only=True)
    price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = ('id', 'ticker', 'isin', 'figi', 'name_asset', 'full_name_asset', 'price', 'currency', 'type_asset',
                  'type_asset_display', 'is_tradable', 'currency_influence', 'created')

    def get_price(self, obj):
        prices_and_currencies = self.context.get('prices_and_currencies', {})
        return prices_and_currencies.get(obj.id, {}).get('price', None)

    def get_currency(self, obj):
        prices_and_currencies = self.context.get('prices_and_currencies', {})
        return prices_and_currencies.get(obj.id, {}).get('currency', None)


class PositionSerializer(serializers.ModelSerializer):
    asset = AssetSerializer()
    total_value = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ('asset', 'account', 'quantity_position', 'total_value')

    def get_total_value(self, obj):
        prices_and_currencies = self.context.get('prices_and_currencies', {})
        price = prices_and_currencies.get(obj.asset.id, {}).get('price', 0)
        return price * obj.quantity_position