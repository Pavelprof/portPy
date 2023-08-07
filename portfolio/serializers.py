from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from .models import Deal, Position, Asset, Account
from .tinkoff_client import get_last_prices

class DealSerializer(serializers.Serializer):
    account = serializers.IntegerField()
    out_asset = serializers.IntegerField()
    in_asset = serializers.IntegerField()
    out_quantity = serializers.FloatField()
    in_quantity = serializers.FloatField()
    lot_exchange_rate = serializers.FloatField()
    exchange = serializers.IntegerField()
    note = serializers.CharField()
    time_deal = serializers.DateTimeField()

def encode():
    model = Deal(account=Account.objects.get(id=2), out_asset=Asset.objects.get(id=2), in_asset=Asset.objects.get(id=1), out_quantity=2, in_quantity=2, exchange=2, note=2)
    model_sr = DealSerializer(model)
    print(model_sr.data, type(model_sr.data), sep='\n')
    json = JSONRenderer().render(model_sr.data)
    print(json)

class AssetSerializer(serializers.ModelSerializer):
    type_asset_display = serializers.CharField(source='get_type_asset_display', read_only=True)
    class Meta:
        model = Asset
        fields = ('id', 'ticker', 'isin', 'figi', 'name_asset', 'full_name_asset', 'type_asset',
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