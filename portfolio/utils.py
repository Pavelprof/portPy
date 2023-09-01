from .api_services import *

def fetch_prices_and_currencies(assets):
    prices_and_currencies = {}

    crypto_assets = [asset for asset in assets if asset.type_asset == 'CO']
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
            data = yfinance_data.get(asset.id, {})
            if data.get('price') in [0, None]:
                prices_and_currencies[asset.id] = {'price': 1, 'currency': asset.ticker}
            else:
                prices_and_currencies[asset.id] = data

    for asset in assets:
        if prices_and_currencies.get(asset.id, {}).get('currency') in [0, None] and asset.currency_base_settlement:
            prices_and_currencies.setdefault(asset.id, {})['currency'] = asset.currency_base_settlement.ticker

    return prices_and_currencies
