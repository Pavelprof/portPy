from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Position, Asset, Transaction, Account
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import math

User = get_user_model()


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user_id = RefreshToken(attrs['refresh']).payload['user_id']
        user = User.objects.get(id=user_id)
        refresh = RefreshToken.for_user(user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data

class AssetSerializer(serializers.ModelSerializer):
    type_asset_display = serializers.CharField(source='get_type_asset_display', read_only=True)
    price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    currency_base_settlement = serializers.CharField(source='currency_base_settlement.ticker')
    currency_influence = serializers.CharField(source='currency_influence.ticker', allow_null=True)

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
    total_value_currency = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ('id', 'asset', 'account', 'quantity_position', 'total_value', 'total_value_currency')

    def get_total_value_currency(self, obj):
        return self.context.get('requested_currency').ticker

    def get_total_value(self, obj):
        prices_and_currencies = self.context.get('prices_and_currencies', {})
        requested_currency = self.context.get('requested_currency')
        price_asset = prices_and_currencies.get(obj.asset.id, {}).get('price', 0)
        settlement_currency = prices_and_currencies.get(obj.asset.id, {}).get('currency', None) #99% it's base_settlement_currency

        if settlement_currency == requested_currency:
            return math.floor(price_asset * obj.quantity_position * 1000) / 1000

        exchange_rate_asset = None

        for asset, asset_info in prices_and_currencies.items(): # Searching for an exchange rate
            currency = asset_info.get('currency')
            currency_influence = asset_info.get('currency_influence')
            type_asset = asset_info.get('type_asset')

            if currency == requested_currency and currency_influence == obj.asset.currency_base_settlement and type_asset == "CY":
                exchange_rate_asset = asset_info.get('price')
                break

        if exchange_rate_asset is None:
            raise ValueError(f"Exchange rate asset not found for {obj.asset.ticker}.")

        return math.floor(price_asset * obj.quantity_position * exchange_rate_asset * 1000) / 1000

class TransactionSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(source='asset_transaction.ticker')
    class Meta:
        model = Transaction
        fields = ('account', 'position', 'ticker', 'quantity_transaction',
                  'type_transaction', 'time_transaction', 'created', 'updated')

class AccountSerializer(serializers.ModelSerializer):
    portfolio = serializers.CharField(source='portfolio.name_portfolio')
    country_account = serializers.SerializerMethodField()
    class Meta:
        model = Account
        fields = ('portfolio', 'name_account', 'country_account', 'broker', 'created')

    def get_country_account(self, obj):
        return obj.country_account.name