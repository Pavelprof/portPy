import django_filters
from django_filters import rest_framework as filters
from django.http import HttpResponseNotFound
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenRefreshView
from django.db.models import Q
from .permissions import isAdminOrReadOnly
from .serializers import *
from .utils import fetch_prices_and_currencies

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

class TransactionFilter(filters.FilterSet):
    account = django_filters.AllValuesMultipleFilter(field_name='account')
    asset_transaction = django_filters.CharFilter(field_name='asset_transaction')
    type_transaction = django_filters.AllValuesMultipleFilter(field_name='type_transaction')
    time_transaction = django_filters.DateTimeFromToRangeFilter(field_name='time_transaction')

    class Meta:
        model = Transaction
        fields = ['account', 'asset_transaction', 'type_transaction', 'time_transaction']

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TransactionFilter

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(account__portfolio__user=user)

    @action(detail=False, methods=['get'])
    def unique_transaction_types(self, request, *args, **kwargs):
        user_transactions = self.queryset.filter(account__portfolio__user=request.user)
        unique_types = user_transactions.order_by().values_list('type_transaction', flat=True).distinct()
        type_display_mapping = dict(Transaction.Types_transaction.choices)
        unique_type_dict = {name: id for id, name in type_display_mapping.items() if id in unique_types}

        return Response(unique_type_dict)

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (isAdminOrReadOnly,)

class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PositionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Position.objects.filter(
            Q(quantity_position__gt=0) | Q(quantity_position__lt=0),
            account__portfolio__user=user
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        requested_currency = Asset.objects.filter(ticker=request.GET.get('settlement_currency', 'USD')).first()
        assets = {instance.asset}

        if instance.asset.currency_base_settlement != requested_currency:
            exchange_rate_asset = Asset.objects.filter(
                type_asset='CY',
                currency_influence=instance.asset.currency_base_settlement,
                currency_base_settlement__ticker=requested_currency
            ).first()

            if exchange_rate_asset:
                assets.add(exchange_rate_asset)

        prices_and_currencies = fetch_prices_and_currencies(assets)

        serializer = self.get_serializer(instance, context={
            'prices_and_currencies': prices_and_currencies,
            'requested_currency': requested_currency
        })
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        requested_currency = Asset.objects.filter(ticker=request.GET.get('settlement_currency', 'USD')).first()
        assets = set(position.asset for position in queryset)

        unique_currency_assets = set(
            position.asset.currency_base_settlement
            for position in queryset
            if position.asset.currency_base_settlement != requested_currency
        )
        for asset in unique_currency_assets:
            exchange_rate_asset = Asset.objects.filter(
                type_asset='CY',
                currency_influence=asset,
                currency_base_settlement__ticker=requested_currency
            ).first()
            if exchange_rate_asset:
                assets.add(exchange_rate_asset)

        prices_and_currencies = fetch_prices_and_currencies(assets)

        serializer = self.get_serializer(queryset, many=True, context={
        'prices_and_currencies': prices_and_currencies,
        'requested_currency': requested_currency
    })
        return Response(serializer.data)


def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Page not found</h1>")

