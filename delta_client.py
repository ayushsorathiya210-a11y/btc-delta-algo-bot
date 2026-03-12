import requests
import time
import hashlib
import hmac
from config import API_KEY, API_SECRET, BASE_URL


class DeltaClient:

    def __init__(self):
        self.base_url = BASE_URL

    def _generate_signature(self, method, timestamp, path, body=""):

        message = method + timestamp + path + body

        signature = hmac.new(
            API_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def _headers(self, signature, timestamp):

        return {
            "api-key": API_KEY,
            "timestamp": timestamp,
            "signature": signature,
            "Content-Type": "application/json"
        }

    def get_balance(self):

        path = "/v2/wallet/balances"
        method = "GET"

        timestamp = str(int(time.time()))

        signature = self._generate_signature(method, timestamp, path)

        headers = self._headers(signature, timestamp)

        r = requests.get(self.base_url + path, headers=headers)

        return r.json()

    def place_order(self, symbol, side, size):

        path = "/v2/orders"
        method = "POST"

        body = f'{{"product_id":1,"size":{size},"side":"{side}","order_type":"market_order"}}'

        timestamp = str(int(time.time()))

        signature = self._generate_signature(method, timestamp, path, body)

        headers = self._headers(signature, timestamp)

        r = requests.post(self.base_url + path, headers=headers, data=body)

        return r.json()
