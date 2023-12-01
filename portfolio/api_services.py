import os
from tinkoff.invest import Client
import requests
import yfinance as yf

def get_quotes_from_tinkoff(figi_list):
    TOKEN = os.environ["TIN_API_KEY"]
    tf_quotes = {}
    with Client(TOKEN) as client:
        r = client.market_data.get_last_prices(figi=figi_list)

        for price_object in r.last_prices:
            figi = price_object.figi
            price = price_object.price.units + price_object.price.nano * 1e-9
            tf_quotes[figi] = {'price': price, 'currency_id': None}

    return tf_quotes

def get_quotes_from_moex(ticker_list):
    def get_moex_quote(ticker):
        base_url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQTF/securities/{ticker}.json?iss.meta=off&iss.json=extended"
        response = requests.get(base_url)
        data = response.json()

        if data[1]['marketdata']:
            marketdata = data[1]['marketdata'][0]
            bid_price = marketdata.get('BID')
            last_price = marketdata.get('LAST')
            quote = bid_price if bid_price is not None else last_price
            return {'price': quote, 'currency_id': None}

        return {'price': None, 'currency_id': None}

    mx_quotes = {}
    for ticker in ticker_list:
        mx_quotes[ticker] = get_moex_quote(ticker)

    return mx_quotes


def get_quotes_from_binance(crypto_tickers):
    base_url = "https://api.binance.com/api/v3/ticker/price"
    bc_quotes = {}

    for ticker in crypto_tickers:
        if ticker == 'USDT':
            bc_quotes[ticker] = {'price': 1, 'currency_id': None}
        else:
            response = requests.get(base_url, params={"symbol": ticker+'USDT'})
            data = response.json()
            if 'symbol' in data and 'price' in data:
                bc_quotes[ticker] = {'price': float(data['price']), 'currency_id': None}

    return bc_quotes


def get_quotes_from_yfinance(ticker_list):
    tkrs = yf.download(ticker_list, period="1d")
    yf_quotes = {}

    if len(ticker_list) == 1:
        last_valid_price = tkrs['Adj Close'].dropna().iloc[-1] if not tkrs['Adj Close'].dropna().empty else None
        if last_valid_price is not None:
            yf_quotes[ticker_list[0]] = {'price': last_valid_price, 'currency_id': None}
    else:
        for ticker in ticker_list:
            ticker_data = tkrs.xs(ticker, level=1, axis=1)
            last_valid_price = ticker_data['Adj Close'].dropna().iloc[-1] if not ticker_data[
                'Adj Close'].dropna().empty else None
            if last_valid_price is not None:
                yf_quotes[ticker] = {'price': last_valid_price, 'currency_id': None}

    return yf_quotes