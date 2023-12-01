from .api_services import *
from django.core.cache import cache
import json
from .models import Asset

def get_price_and_currency(asset_id):
    price_and_currency_json = cache.get(f'asset_info:{asset_id}')
    if price_and_currency_json is not None:
        return {asset_id: json.loads(price_and_currency_json)}

    asset = Asset.objects.get(id=asset_id)
    price_and_currency_data = fetch_prices_and_currencies([asset])

    cache.set(f'asset_info:{asset_id}', json.dumps(price_and_currency_data[asset_id]), 900)

    return price_and_currency_data

def fetch_prices_and_currencies(assets):
    prices_and_currencies = {}

    zero_assets = [asset for asset in assets if asset.is_tradable == False]
    if zero_assets:
        for asset in zero_assets:
            prices_and_currencies[asset.id] = {'price': 0, 'currency_id': asset.currency_base_settlement.id}

    unit_assets = [asset for asset in assets if (asset.type_asset == 'CY' and asset.currency_influence == asset.currency_base_settlement)]
    if unit_assets:
        for asset in unit_assets:
            prices_and_currencies[asset.id] = {'price': 1, 'currency_id': asset.currency_base_settlement.id}


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
            prices_and_currencies.setdefault(asset.id, {})['currency_id'] = asset.currency_base_settlement.id

        if asset.type_asset == 'BD':
            prices_and_currencies.setdefault(asset.id, {})['price'] *= (float(asset.bond_nominal)/100)


    return prices_and_currencies
