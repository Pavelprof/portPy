import json
from django.core.cache import cache
from celery import shared_task
from portfolio.models import Position, Asset
from portfolio.utils import fetch_prices_and_currencies
from django.db.models import Q, F

@shared_task
def update_asset_prices(asset_ids=None):
    if asset_ids:
        queryset_assets = Asset.objects.filter(id__in=asset_ids)
    else:
        asset_ids = Position.objects.exclude(quantity_position=0).values_list('asset_id', flat=True).distinct()
        additional_condition = Q(type_asset='CY') & ~Q(currency_influence_id=F('currency_base_settlement_id'))
        queryset_assets = Asset.objects.filter(Q(id__in=asset_ids) | additional_condition)

    prices_info = fetch_prices_and_currencies(queryset_assets)

    for asset_id, asset_info in prices_info.items():
        cache.set(f'asset_info:{asset_id}', json.dumps(asset_info), 7200)