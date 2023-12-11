from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Position, Asset, Transaction, Account
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .utils import get_price_and_currency

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
    currency_base_settlement = serializers.CharField(source='currency_base_settlement.ticker')
    currency_influence = serializers.CharField(source='currency_influence.ticker', allow_null=True)

    class Meta:
        model = Asset
        fields = ('id', 'ticker', 'isin', 'figi', 'name_asset', 'full_name_asset', 'currency_base_settlement', 'type_asset',
                  'type_asset_display', 'is_tradable', 'currency_influence', 'created')


class PositionSerializer(serializers.ModelSerializer):
    asset = AssetSerializer(read_only=True)
    price = serializers.FloatField(read_only=True)
    price_currency = serializers.CharField(read_only=True)
    position_value = serializers.FloatField(read_only=True)
    position_value_currency = serializers.CharField(read_only=True)

    class Meta:
        model = Position
        fields = ('id', 'asset', 'account', 'price', 'price_currency', 'quantity_position', 'position_value', 'position_value_currency')

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        price_and_currency = get_price_and_currency(instance.asset_id)
        requested_currency = self.context.get('requested_currency')
        price = price_and_currency[instance.asset_id]['price']

        representation['price'] = price
        representation['price_currency'] = price_and_currency[instance.asset_id]['currency']['ticker']
        representation['position_value_currency'] = requested_currency.ticker

        if price_and_currency[instance.asset_id]['currency']['ticker'] == requested_currency:
            representation['position_value'] = instance.quantity_position * price
        else:
            exchange_rate_asset = Asset.objects.filter(
                type_asset='CY',
                currency_influence=instance.asset.currency_base_settlement,
                currency_base_settlement__ticker=requested_currency
            ).first()
            exchange_rate = get_price_and_currency(exchange_rate_asset.id)[exchange_rate_asset.id]['price']
            representation['position_value'] = instance.quantity_position * price * exchange_rate

        return representation

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