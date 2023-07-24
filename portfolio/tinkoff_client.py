from tinkoff.invest import Client

class TinkoffClient:
    def __init__(self, token):
        self.token = token

    def get_instrument_price(self, figis):
        with Client(self.token) as client:
