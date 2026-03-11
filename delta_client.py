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
            "api-key": API_KEY,
            "timestamp": timestamp,
            "signature": signature,
            "Content-Type": "application/json"
        }

    def get_balance(self):

        path = "/v2/wallet/balances"
        url = self.base_url + path

        headers = self._generate_headers("GET", path)

        try:

            r = requests.get(url, headers=headers, timeout=10)

            print("[API] Balance status:", r.status_code)

            data = r.json()

            if not data.get("success"):
                print("[ERROR] Balance API:", data)

            return data

        except Exception as e:

            print("[ERROR] Balance request failed:", str(e))

            return {"success": False, "error": str(e)}

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

        try:

            r = requests.post(
                url,
                headers=headers,
                data=body_json,
                timeout=10
            )

            print("[API] Order status:", r.status_code)

            return r.json()

        except Exception as e:

            print("[ERROR] Order request failed:", str(e))

            return {"success": False, "error": str(e)}
