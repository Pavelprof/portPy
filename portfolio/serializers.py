from rest_framework import serializers
from .models import Deal, Position, Asset
from .tinkoff_client import get_last_prices
class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ('id', 'account', 'out_asset', 'in_asset', 'out_quantity',
                  'in_quantity', 'time_deal', 'note')

class AssetSerializer(serializers.ModelSerializer):
    type_asset_display = serializers.CharField(source='get_type_asset_display', read_only=True)

    class Meta:
        model = Asset
        fields = ('id', 'ticker', 'isin', 'figi', 'name_asset', 'issuer', 'country', 'type_asset',
                 'type_asset_display', 'is_tradable', 'currency_influence', 'created')

class PositionSerializer(serializers.ModelSerializer):
    asset = AssetSerializer()

    price = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ('asset', 'account', 'quantity_position', 'price', 'total_value')

    def get_price(self, obj):
        figi_list = [obj.asset.figi]
        prices = get_last_prices(figi_list)
        price_info = prices.get(obj.asset.figi)
        if price_info:
            price = price_info.price.units + price_info.price.nano / 1e9
            return price
        return None

    def get_total_value(self, obj):
        price = self.get_price(obj)
        if price is not None:
            return obj.quantity_position * price
        return None