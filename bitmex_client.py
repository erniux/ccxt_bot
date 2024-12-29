import logging
import requests
import secrets_1
from urllib.parse import urlencode
import hmac
import hashlib
import time


logger = logging.getLogger()


class BitmexClient:
    def __init__(self, testnet):
        if testnet:
            self._base_url = secrets_1.BITMEX_SPOT_TESTNET_URL
            self._wss_url = secrets_1.BITMEX_SPOT_TESTNET_WS_URL
            self._api_key = secrets_1.BITMEX_SPOT_TESTNET_API_KEY
            self._secret_key = secrets_1.BITMEX_SPOT_TESTNET_SECRET_KEY
        else:
            self._base_url = secrets_1.BITMEX_SPOT_API_URL
            self._wss_url = secrets_1.BITMEX_SPOT_WS_URL
            self._api_key = ''
            self._secret_key = ''

    def _generate_signature(self, method, endpoint, expires, data):
        if len(data) > 0:
            message = method + endpoint + "?" + urlencode(data) + expires 
        else: 
            message = method + endpoint + expires
            
        return hmac.new(self._secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()

    def _make_request(self, method, endpoint, data):
        headers = dict()
        expires = str(int(time.time() + 5))
        headers['api-expires'] = expires
        headers['api-key'] = self._api_key
        headers['api-signature'] = self._generate_signature(method, endpoint, expires, data)
        
        if method == 'GET':
            try:
                response = requests.get(self._base_url + endpoint, params=data, headers=headers)
            except Exception as e:
                logger.error(f"Error en conexion al hacer {method} a {endpoint} : {e}")
        elif method == 'POST':
            try:
                response = requests.post(self._base_url + endpoint, params=data, headers=headers)
            except Exception as e:
                logger.error(f"Error en conexion al hacer {method} a {endpoint} : {e}")
        elif method == 'DELETE':
            try:
                response = requests.delete(self._base_url + endpoint, params=data, headers=headers)
            except Exception as e:
                logger.error(f"Error en conexion al hacer {method} a {endpoint} : {e}")
        else:
            raise ValueError()

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"ERROR EN REQUEST {method}, {endpoint}: {response.json()}, {response.status_code}, {response.request.headers} ")


    def get_contracts(self):
        data = []
        instruments = self._make_request("GET", "/api/v1/instrument/active", data)
        contracts = dict()

        if instruments is not None:

            for contract_data in instruments:
                contracts[contract_data['symbol']] = contract_data

        return contracts
        
 
    def get_historical_candles(self, contract, timeframe):
        pass
        
    def get_balances(self):
        data = dict()
        data['currency'] = "all"
        account_data = self._make_request("GET", "/api/v1/user/margin", data)

        balances = dict()
        if account_data is not None:
            for a in account_data:
                balances[a['currency']] = a

        return balances
        
    def place_order(self, symbol, order_type, quantity, side):
        data = dict()
        data['symbol'] = symbol
        data['side'] = side 
        data['orderQty'] = quantity
        data['orderType'] = order_type 

        order_status = self._make_request("POST", "/api/v1/order", data)

        if order_status is not None:
            order_status = order_status

        return order_status

	