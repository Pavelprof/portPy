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
            tf_quotes[figi] = {'price': price, 'currency': None}

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
            return {'price': quote, 'currency': None}

        return {'price': None, 'currency': None}

    mx_quotes = {}
    for ticker in ticker_list:
        mx_quotes[ticker] = get_moex_quote(ticker)

    return mx_quotes


def get_quotes_from_binance(crypto_tickers):
    base_url = "https://api.binance.com/api/v3/ticker/price"
    bc_quotes = {}

    for ticker in crypto_tickers:
        if ticker == 'USDT':
            bc_quotes[ticker] = {'price': 1, 'currency': None}
        else:
            response = requests.get(base_url, params={"symbol": ticker+'USDT'})
            data = response.json()
            if 'symbol' in data and 'price' in data:
                bc_quotes[ticker] = {'price': float(data['price']), 'currency': None}

    return bc_quotes


def get_quotes_from_yfinance(ticker_list):
    tkrs = yf.download(ticker_list, period="1d")
    yf_quotes = {}

    if len(ticker_list) == 1:
        tickers_yf = {ticker_list[0]: tkrs['Adj Close'].iloc[-1]}
    else:
        tickers_series = tkrs['Adj Close'].iloc[-1]
        tickers_yf = tickers_series.to_dict()

    for ticker in tickers_yf:
        if tickers_yf[ticker]:
            yf_quotes[ticker] = {'price': tickers_yf[ticker], 'currency': None}
    return yf_quotes