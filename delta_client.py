import requests
import time
import hmac
import hashlib
import json
from config import API_KEY, API_SECRET, BASE_URL

class DeltaClient:

    def __init__(self):
        self.base_url = BASE_URL

    def _generate_headers(self, method, path, body=""):
        timestamp = str(int(time.time() * 1000))
        message = timestamp + method + path + body
        signature = hmac.new(
            API_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return {
            "APIKEY": API_KEY,
            "SIGNATURE": signature,
            "TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        }

    def get_balance(self):
        path = "/v2/wallet/balances"
        url = self.base_url + path
        headers = self._generate_headers("GET", path)
        return requests.get(url, headers=headers).json()

    def get_positions(self):
        path = "/v2/positions"
        url = self.base_url + path
        headers = self._generate_headers("GET", path)
        return requests.get(url, headers=headers).json()

    def place_market_order(self, symbol, side, size):
        path = "/v2/orders"
        url = self.base_url + path

        body = {
            "symbol": symbol,
            "side": side,
            "order_type": "market",
            "size": size,
            "time_in_force": "IOC"
        }

        body_json = json.dumps(body)
        headers = self._generate_headers("POST", path, body_json)

        response = requests.post(url, headers=headers, data=body_json)
        return response.json()