import django_filters
from django_filters import rest_framework as filters
from django.http import HttpResponseNotFound
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenRefreshView
from django.db.models import Q, F
from .models import AssetGroup
from .permissions import isAdminOrReadOnly
from .serializers import *
from .utils import get_price_and_currency, apply_assetgroup_filters


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

class PositionFilter(filters.FilterSet):
    ticker = django_filters.CharFilter(field_name='asset__ticker')
    isin = django_filters.CharFilter(field_name='asset__isin')
    currency_influence = django_filters.CharFilter(field_name='asset__currency_influence')
    type_asset = django_filters.AllValuesMultipleFilter(field_name='asset__type_asset')
    account = django_filters.AllValuesMultipleFilter(field_name='account')

    class Meta:
        model = Position
        fields = ['ticker', 'isin', 'currency_influence', 'type_asset', 'account']

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
        user_transactions = self.get_queryset().filter(account__portfolio__user=request.user)
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
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PositionFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['requested_currency'] = Asset.objects.filter(ticker=self.request.GET.get('settlement_currency', 'USD')).first()
        return context

    def get_queryset(self):
        user = self.request.user
        queryset = Position.objects.filter(
            Q(quantity_position__gt=0) | Q(quantity_position__lt=0),
            account__portfolio__user=user
        )

        return queryset

    @action(detail=False, methods=['get'])
    def structure(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        user = request.user
        requested_structure_id = request.query_params.get('structure_id')
        requested_currency = Asset.objects.filter(ticker=self.request.GET.get('settlement_currency', 'USD')).first()
        total_positions_value = 0
        group_data = {}
        group_targets = {}
        other_group_fact_value = 0

        for position in queryset:
            price_and_currency = get_price_and_currency(position.asset_id)
            price = price_and_currency[position.asset_id]['price']

            position.price_currency = price_and_currency[position.asset_id]['currency']['ticker']
            position.price = price
            position.total_value_currency = requested_currency

            if price_and_currency[position.asset_id]['currency']['ticker'] == requested_currency:
                position.total_value = position.quantity_position * position.price
            else:
                exchange_rate_asset = Asset.objects.filter(
                    type_asset='CY',
                    currency_influence=position.asset.currency_base_settlement,
                    currency_base_settlement__ticker=requested_currency
                ).first()
                exchange_rate = get_price_and_currency(exchange_rate_asset.id)[exchange_rate_asset.id]['price']
                position.total_value = position.quantity_position * position.price * exchange_rate

            total_positions_value += position.total_value

        # for group in AssetGroup.objects.filter(targetweight__structure_id=requested_structure_id):
        #     group_queryset = queryset.apply_assetgroup_filters(group.filters)


        return Response(total_positions_value)


    @action(detail=False, methods=['get'])
    def unique_asset_types(self, request):
        unique_types_query = self.get_queryset().values_list('asset__type_asset', flat=True).distinct()

        type_display_mapping = dict(Asset.TYPE_ASSET_CHOICES)

        unique_asset_types = {
            type_display_mapping[type_code]:type_code
            for type_code in unique_types_query if type_code in type_display_mapping
        }

        return Response(unique_asset_types)

class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Account.objects.filter(portfolio__user=user)

def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Page not found</h1>")

