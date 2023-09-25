import django_filters
from django_filters import rest_framework as filters
from django.http import HttpResponseNotFound
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .permissions import isAdminOrReadOnly, IsOwner
from .serializers import *
from .utils import fetch_prices_and_currencies

class ListFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass

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
        settlement_currency = Asset.objects.filter(ticker=request.GET.get('settlement_currency', 'USD')).first()
        assets = {instance.asset}

        if instance.asset.currency_base_settlement != settlement_currency:
            exchange_rate_asset = Asset.objects.filter(
                type_asset='CY',
                currency_influence=instance.asset.currency_base_settlement,
                currency_base_settlement__ticker=settlement_currency
            ).first()

            if exchange_rate_asset:
                assets.add(exchange_rate_asset)

        prices_and_currencies = fetch_prices_and_currencies(assets)

        serializer = self.get_serializer(instance, context={
            'prices_and_currencies': prices_and_currencies,
            'settlement_currency': settlement_currency
        })
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        settlement_currency = Asset.objects.filter(ticker=request.GET.get('settlement_currency', 'USD')).first()
        assets = set(position.asset for position in queryset)

        unique_currency_assets = set(
            position.asset.currency_base_settlement
            for position in queryset
            if position.asset.currency_base_settlement != settlement_currency
        )
        for asset in unique_currency_assets:
            exchange_rate_asset = Asset.objects.filter(
                type_asset='CY',
                currency_influence=asset,
                currency_base_settlement__ticker=settlement_currency
            ).first()
            if exchange_rate_asset:
                assets.add(exchange_rate_asset)

        prices_and_currencies = fetch_prices_and_currencies(assets)

        serializer = self.get_serializer(queryset, many=True, context={
        'prices_and_currencies': prices_and_currencies,
        'settlement_currency': settlement_currency
    })
        return Response(serializer.data)

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (isAdminOrReadOnly,)

class TransactionFilter(filters.FilterSet):
    account__in = ListFilter(field_name='account', lookup_expr='in')
    asset_transaction = django_filters.CharFilter(field_name='asset_transaction')
    type_transaction__in = ListFilter(field_name='type_transaction', lookup_expr='in')
    time_transaction = django_filters.DateTimeFromToRangeFilter(field_name='time_transaction')

    class Meta:
        model = Transaction
        fields = []

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    # permission_classes = (IsOwner,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TransactionFilter

def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Page not found</h1>")

