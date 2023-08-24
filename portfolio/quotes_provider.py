import os
from tinkoff.invest import Client
import requests
import yfinance as yf

def get_quotes_from_tinkoff(figi_list):
    TOKEN = os.environ["TIN_API_KEY"]
    with Client(TOKEN) as client:
        r = client.market_data.get_last_prices(figi=figi_list)
        tf_quotes = {price.figi: price for price in r.last_prices}
        return tf_quotes

def get_quotes_from_moex(ticker_list):
    def get_moex_quote(ticker):
        base_url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQTF/securities/{ticker}.json?iss.meta=off&iss.json=extended"
        response = requests.get(base_url)
        data = response.json()

        if len(data) > 1 and 'marketdata' in data[1]:
            marketdata = data[1]['marketdata'][0]
            bid_price = marketdata.get('BID')
            last_price = marketdata.get('LAST')

            return bid_price if bid_price is not None else last_price
        return None

    mx_quotes = {}
    for ticker in ticker_list:
        mx_quotes[ticker] = get_moex_quote(ticker)

    return mx_quotes


def get_quotes_from_binance(ticker_list):
    base_url = "https://api.binance.com/api/v3/ticker/price"
    bc_quotes = {}

    for ticker in ticker_list:
        response = requests.get(base_url, params={"symbol": ticker})
        data = response.json()
        if 'symbol' in data and 'price' in data:
            bc_quotes[data['symbol']] = float(data['price'])

    return bc_quotes


def get_quotes_from_yfinance(ticker_list):
    tkrs = yf.download(ticker_list, period="1m")
    current_prices_series = tkrs['Adj Close'].iloc[-1]
    yf_quotes = current_prices_series.to_dict()
    return yf_quotes