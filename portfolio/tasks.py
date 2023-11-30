import json
from django.core.cache import cache
from celery import shared_task
from portfolio.models import Position, Asset
from portfolio.utils import fetch_prices_and_currencies

@shared_task
def update_asset_prices():
    asset_ids = Position.objects.exclude(quantity_position=0).values_list('asset_id', flat=True).distinct()
    assets = Asset.objects.filter(id__in=asset_ids)

    prices_info = fetch_prices_and_currencies(assets)

    for asset_id, asset_info in prices_info.items():
        asset_info_for_json = {
            'price': asset_info['price'],
            'currency_id': asset_info['currency'].id if asset_info['currency'] else None,
            'currency_influence_id': asset_info['currency_influence'].id if asset_info['currency_influence'] else None,
            'type_asset': asset_info['type_asset']
        }

        asset_info_json = json.dumps(asset_info_for_json)
        cache.set(f'asset_info:{asset_id}', asset_info_json)