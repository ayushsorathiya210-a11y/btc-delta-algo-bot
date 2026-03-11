import requests
import time
import hashlib
import hmac
from config import API_KEY, API_SECRET, BASE_URL


class DeltaClient:

    def __init__(self):
        self.base_url = BASE_URL

    def _generate_signature(self, method, timestamp, path, query_string="", body=""):

        message = method + timestamp + path + query_string + body

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

    # =========================
    # GET BALANCE
    # =========================
    def get_balance(self):

        method = "GET"
        path = "/v2/wallet/balances"
        query_string = ""
        body = ""

        timestamp = str(int(time.time()))

        signature = self._generate_signature(
            method, timestamp, path, query_string, body
        )

        headers = self._headers(signature, timestamp)

        url = self.base_url + path

        r = requests.get(url, headers=headers)

        print("[API] Balance status:", r.status_code)

        return r.json()

    # =========================
    # PLACE ORDER
    # =========================
    def place_order(self, symbol, side, size):

        method = "POST"
        path = "/v2/orders"
        query_string = ""

        body = f'{{"product_id":1,"size":{size},"side":"{side}","order_type":"market_order"}}'

        timestamp = str(int(time.time()))

        signature = self._generate_signature(
            method, timestamp, path, query_string, body
        )

        headers = self._headers(signature, timestamp)

        url = self.base_url + path

        r = requests.post(url, headers=headers, data=body)

        return r.json()
