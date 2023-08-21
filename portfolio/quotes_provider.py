import os
from tinkoff.invest import Client
import requests

def get_quotes_from_tinkoff(figi_list):
    TOKEN = os.environ["TIN_API_KEY"]
    with Client(TOKEN) as client:
        r = client.market_data.get_last_prices(figi=figi_list)
        quotes = {price.figi: price for price in r.last_prices}
        return quotes

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

    quotes = {}
    for ticker in ticker_list:
        quotes[ticker] = get_moex_quote(ticker)

    return quotes

def get_quotes_from_binance(ticker_list):
    pass

def get_quotes_from_yfinance(ticker_list):
    pass