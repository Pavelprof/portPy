from .api_services import *
from django.core.cache import cache
import json
from .models import Asset
from django.db.models import Q

def apply_assetgroup_filters(filters_json):
    q_objects = Q()

    for criterion in filters_json:
        field = f'asset__{criterion.get("field")}'
        operation = criterion.get('operation')
        value = criterion.get('value')

        if operation == 'equals':
            q_objects &= Q(**{field: value})
        elif operation == 'not_equals':
            q_objects &= ~Q(**{field: value})
        elif operation == 'in':
            q_objects &= Q(**{f'{field}__in': value})
        elif operation == 'not_in':
            q_objects &= ~Q(**{f'{field}__in': value})
        elif operation == 'less_than':
            q_objects &= Q(**{f'{field}__lt': value})
        elif operation == 'less_than_or_equal_to':
            q_objects &= Q(**{f'{field}__lte': value})
        elif operation == 'greater_than':
            q_objects &= Q(**{f'{field}__gt': value})
        elif operation == 'greater_than_or_equal_to':
            q_objects &= Q(**{f'{field}__gte': value})
        elif operation == 'contains':
            q_objects &= Q(**{f'{field}__contains': value})
        elif operation == 'not_contains':
            q_objects &= ~Q(**{f'{field}__contains': value})

    return q_objects

def get_price_and_currency(asset_id, quantity=None, value_currency_id=None, value_currency_ticker=None):
    price_and_currency_json = cache.get(f'asset_info:{asset_id}')
    if price_and_currency_json is not None:
        price_and_currency = json.loads(price_and_currency_json)

    else:
        asset = Asset.objects.get(id=asset_id)
        price_and_currency = fetch_prices_and_currencies([asset])
        price_and_currency = price_and_currency[asset_id]
        cache.set(f'asset_info:{asset_id}', json.dumps(price_and_currency), 900)

    if quantity is None or value_currency_id is None:
        return {asset_id: price_and_currency}

    if 'price' not in price_and_currency:
        print("data in cash without price!!!") # ToDo
    asset_price = price_and_currency['price']
    asset_currency_id = price_and_currency['currency']['id']

    if asset_currency_id == value_currency_id:
        value = quantity * asset_price
    else:
        exchange_rate_asset = Asset.objects.filter(type_asset='CY',
            currency_influence=asset_currency_id,
            currency_base_settlement=value_currency_id
        ).first()
        exchange_rate = get_price_and_currency(exchange_rate_asset.id)[exchange_rate_asset.id]["price"]
        value = quantity * asset_price * exchange_rate

    price_and_currency['quantity'] = quantity
    price_and_currency['value'] = value
    price_and_currency['value_currency'] = {'id': value_currency_id,
                                            'ticker': value_currency_ticker if value_currency_ticker else Asset.objects.get(id=value_currency_id).ticker}

    return {asset_id: price_and_currency}

def fetch_prices_and_currencies(assets):
    prices_and_currencies = {}

    zero_assets = [asset for asset in assets if asset.is_tradable == False]
    if zero_assets:
        for asset in zero_assets:
            prices_and_currencies[asset.id] = {'price': 0, 'currency': {'id': asset.currency_base_settlement.id, 'ticker':asset.currency_base_settlement.ticker}}

    unit_assets = [asset for asset in assets if (asset.type_asset == 'CY' and asset.currency_influence == asset.currency_base_settlement)]
    if unit_assets:
        for asset in unit_assets:
            prices_and_currencies[asset.id] = {'price': 1, 'currency': {'id': asset.currency_base_settlement.id, 'ticker':asset.currency_base_settlement.ticker}}


    crypto_assets = [asset for asset in assets if asset.type_asset == 'CO' and asset.id not in prices_and_currencies]
    if crypto_assets:
        crypto_tickers = [asset.ticker for asset in crypto_assets]
        binance_data = get_quotes_from_binance(crypto_tickers)
        for asset in crypto_assets:
            data = binance_data.get(asset.ticker, {})
            if data.get('price') not in [0, None]:
                prices_and_currencies[asset.id] = data

    figi_assets = [asset for asset in assets if asset.figi and asset.id not in prices_and_currencies]
    if figi_assets:
        figi_list = [asset.figi for asset in figi_assets]
        tinkoff_data = get_quotes_from_tinkoff(figi_list)
        for asset in figi_assets:
            data = tinkoff_data.get(asset.figi, {})
            if data.get('price') not in [0, None]:
                prices_and_currencies[asset.id] = data

    class_code_assets = [asset for asset in assets if asset.class_code and asset.id not in prices_and_currencies]
    if class_code_assets:
        ticker_list = [asset.ticker for asset in class_code_assets]
        moex_data = get_quotes_from_moex(ticker_list)
        for asset in class_code_assets:
            data = moex_data.get(asset.ticker, {})
            if data.get('price') not in [0, None]:
                prices_and_currencies[asset.id] = data

    remaining_assets = [asset for asset in assets if asset.id not in prices_and_currencies]
    if remaining_assets:
        ticker_list = [asset.ticker for asset in remaining_assets]
        yfinance_data = get_quotes_from_yfinance(ticker_list)
        for asset in remaining_assets:
            data = yfinance_data.get(asset.ticker, {})
            if data.get('price') not in [0, None]:
                prices_and_currencies[asset.id] = data

    for asset in assets:
        if prices_and_currencies.get(asset.id, {}).get('currency') in [0, None]:
            prices_and_currencies.setdefault(asset.id, {})['currency'] = {'id': asset.currency_base_settlement.id, 'ticker':asset.currency_base_settlement.ticker}

        if asset.type_asset == 'BD':
            prices_and_currencies.setdefault(asset.id, {})['price'] *= (float(asset.bond_nominal)/100)


    return prices_and_currencies
