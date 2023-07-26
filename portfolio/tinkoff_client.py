import os
from tinkoff.invest import Client

def get_last_prices(figi_list):
    TOKEN = os.environ["TIN_API_KEY"]
    with Client(TOKEN) as client:
        r = client.market_data.get_last_prices(figi=figi_list)
        return {price.figi: price for price in r.last_prices}