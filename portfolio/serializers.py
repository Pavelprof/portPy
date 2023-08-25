from rest_framework import serializers
from .models import Deal, Position, Asset, Transaction
from .quotes_provider import *

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
        price = None
        country = obj.account.country_account
        asset = obj.asset

        if not asset.is_tradable:
            pass
        elif country == "RU":
            if asset.figi:
                figi_prices = get_quotes_from_tinkoff([asset.figi])
                if figi_prices and figi_prices.get(asset.figi) not in [0, None]:
                    price = figi_prices[asset.figi]
                else:
                    moex_prices = get_quotes_from_moex([asset.ticker])
                    price = moex_prices.get(asset.ticker)
            else:
                moex_prices = get_quotes_from_moex([asset.ticker])
                price = moex_prices.get(asset.ticker)
        elif not country:
            binance_prices = get_quotes_from_binance([asset.ticker])
            price = binance_prices.get(asset.ticker)
        else:
            yfinance_prices = get_quotes_from_yfinance([asset.ticker])
            price = yfinance_prices.get(asset.ticker)

        return price

    def get_total_value(self, obj):
        price = self.get_price(obj)
        if price is not None:
            return obj.quantity_position * price
        return None