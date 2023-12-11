import django_filters
from django_filters import rest_framework as filters
from django.http import HttpResponseNotFound
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenRefreshView
from django.db.models import Q, F
from .models import AssetGroup, TargetWeight
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
        requested_currency = Asset.objects.filter(ticker=request.query_params.get('settlement_currency', 'USD')).first()
        positions_with_groups = {}
        overlapping_positions = []
        total_positions_value = 0
        group_data = []
        ungrouped_positions = []

        for group in AssetGroup.objects.filter(targetweight__structure_id=requested_structure_id):
            group_queryset = queryset.filter(apply_assetgroup_filters(group.filters))
            group_positions = []
            group_value = 0

            for position in group_queryset:
                price_and_currency = get_price_and_currency(position.asset_id)

                position_price_currency = price_and_currency[position.asset_id]['currency']['ticker']
                position_price = price_and_currency[position.asset_id]['price']
                position_value_currency = requested_currency.ticker

                if position_price_currency == requested_currency:
                    position_value = position.quantity_position * position_price
                else:
                    exchange_rate_asset = Asset.objects.filter(
                        type_asset='CY',
                        currency_influence=position.asset.currency_base_settlement,
                        currency_base_settlement__ticker=requested_currency
                    ).first()
                    exchange_rate = get_price_and_currency(exchange_rate_asset.id)[exchange_rate_asset.id]['price']
                    position_value = position.quantity_position * position_price * exchange_rate

                position_data = {
                    "position_id": position.id,
                    "asset_id": position.asset_id,
                    "ticker": position.asset.ticker,
                    "exchange": position.asset.exchange,
                    "quantity_position": position.quantity_position,
                    "position_value": position_value,
                    "position_value_currency": position_value_currency
                }

                group_value += position_value
                group_positions.append(position_data)

                if position.id not in positions_with_groups:
                    position_data_for_overlap = position_data.copy()
                    positions_with_groups[position.id] = position_data_for_overlap
                    positions_with_groups[position.id]["groups"] = []
                    total_positions_value += position_value

                positions_with_groups[position.id]["groups"].append({
                    "group_id": group.id,
                    "group_name": group.name
                })

            group_data.append({
                "group_id": group.id,
                "group_name": group.name,
                "target_weight": TargetWeight.objects.filter(structure=requested_structure_id,
                                                             asset_group=group.id).first().target_weight,
                "group_value": group_value,
                "group_value_currency": requested_currency.ticker,
                "group_positions": group_positions,
            })

        for position in queryset:
            if position.id not in positions_with_groups:
                position_data = create_position_data(position)  # ToDo
                ungrouped_positions.append(position_data)

        group_data.append({
            "group_id": None,
            "group_name": "Ungrouped Assets",
            "target_weight": 0,
            "group_value": sum(pos["position_value"] for pos in ungrouped_positions),
            "group_value_currency": requested_currency.ticker,
            "group_positions": ungrouped_positions,
        })

        overlapping_positions = [
            position_info for position_info in positions_with_groups.values() if len(position_info["groups"]) > 1
        ]

        return Response([group_data, overlapping_positions])


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

