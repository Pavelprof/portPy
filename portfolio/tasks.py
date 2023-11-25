import json
from django.conf import settings
from celery import shared_task
from .models import Position, Asset
from .utils import fetch_prices_and_currencies
import redis

r = redis.Redis.from_url(settings.REDIS_CACHE_URL)

@shared_task
def update_asset_prices():
    asset_ids = Position.objects.exclude(quantity_position=0).values_list('asset_id', flat=True).distinct()
    assets = Asset.objects.filter(id__in=asset_ids)

    prices_info = fetch_prices_and_currencies(assets)

    for asset_id, asset_info in prices_info.items():
        r.set(f'asset_info:{asset_id}', json.dumps(asset_info))