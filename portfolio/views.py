import django_filters
from django_filters import rest_framework as filters
from django.http import HttpResponseNotFound
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenRefreshView
from django.db.models import Q, F
from .models import AssetGroup, TargetWeight, Structure
from .permissions import isAdminOrReadOnly
from .serializers import *
from .utils import get_price_and_currency, apply_assetgroup_filters
from decimal import Decimal

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
        context['requested_currency_id'] = self.request.GET.get('settlement_currency', 1)
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
        requested_currency = Asset.objects.get(id=request.query_params.get('settlement_currency', 1))
        requested_structure_id = request.query_params.get('structure', 1)
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
                price_and_currency = get_price_and_currency(position.asset_id, position.quantity_position, requested_currency.id, requested_currency.ticker)

                position_data = {
                    "position_id": position.id,
                    "exchange": {
                        "id": position.exchange_id,
                        "name": position.exchange.name,
                    },
                    "asset": {
                        "id": position.asset_id,
                        "ticker": position.asset.ticker,
                        "asset_price": price_and_currency[position.asset_id]['price'],
                        "asset_price_currency": price_and_currency[position.asset_id]['currency']['ticker'],
                    },
                    "quantity_position": position.quantity_position,
                    "position_value": price_and_currency[position.asset_id]['value'],
                    "position_value_currency": price_and_currency[position.asset_id]['value_currency']['ticker']
                }

                group_value += price_and_currency[position.asset_id]['value']
                group_positions.append(position_data)

                if position.id not in positions_with_groups:
                    total_positions_value += price_and_currency[position.asset_id]['value']

                    position_data_for_overlap = position_data.copy()
                    positions_with_groups[position.id] = position_data_for_overlap
                    positions_with_groups[position.id]["groups"] = []

                positions_with_groups[position.id]["groups"].append({
                    "group_id": group.id,
                    "group_name": group.name
                })

            group_data.append({
                "group_id": group.id,
                "group_name": group.name,
                "group_value": group_value,
                "group_value_currency": requested_currency.ticker,
                "group_positions": group_positions,
                "target_weight": TargetWeight.objects.filter(structure=requested_structure_id,
                                                             asset_group=group.id).first().target_weight,
            })

        for position in queryset:
            if position.id not in positions_with_groups:
                price_and_currency = get_price_and_currency(position.asset_id, position.quantity_position,
                                                            requested_currency.id, requested_currency.ticker)

                position_data = {
                    "position_id": position.id,
                    "exchange": {
                        "id": position.exchange_id,
                        "name": position.exchange.name,
                    },
                    "asset": {
                        "id": position.asset_id,
                        "ticker": position.asset.ticker,
                        "asset_price": price_and_currency[position.asset_id]['price'],
                        "asset_price_currency": price_and_currency[position.asset_id]['currency']['ticker'],
                    },
                    "quantity_position": position.quantity_position,
                    "position_value": price_and_currency[position.asset_id]['value'],
                    "position_value_currency": price_and_currency[position.asset_id]['value_currency']['ticker']
                }

                total_positions_value += price_and_currency[position.asset_id]['value']

                ungrouped_positions.append(position_data)

        group_data.append({
            "group_id": None,
            "group_name": "Ungrouped Assets",
            "target_weight": 0,
            "group_value": sum(pos["position_value"] for pos in ungrouped_positions),
            "group_value_currency": requested_currency.ticker,
            "group_positions": ungrouped_positions,
        })

        for group in group_data:
            group["weight"] = group["group_value"] / total_positions_value * 100
            group["change"] = group["target_weight"] - Decimal(group["weight"])

        overlapping_positions = [
            position_info for position_info in positions_with_groups.values() if len(position_info["groups"]) > 1
        ]

        return Response({"groups": group_data, "overlapping_positions": overlapping_positions, "total_positions":{"value": total_positions_value, "currency": requested_currency.ticker}})


    @action(detail=False, methods=['get'])
    def unique_asset_types(self, request):
        unique_types_query = self.get_queryset().values_list('asset__type_base_asset', flat=True).distinct()

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

class StructureViewSet(viewsets.ModelViewSet):
    serializer_class = StructureSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Structure.objects.filter(Q(owner=user) | Q(isPublic=True))

def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Page not found</h1>")

