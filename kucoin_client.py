import base64
import time
import requests
from urllib.parse import urlencode
import hmac
import hashlib
import ccxt
import websocket
import threading
import json
import logging
import typing
import secrets


logger = logging.getLogger()


class KucoinClient:
    def __init__(self, testnet: bool):

        if testnet:
            self._base_url = secrets.KUCOIN_SANDBOX_API_URL
            self._wss_url = secrets.KUCOIN_SANDBOX_WS_URL
            self._api_key = secrets.KUCOIN_SANDBOX_API_KEY
            self._secret_key = secrets.KUCOIN_SANDBOX_SECRET_KEY
            self._passphrase_key = secrets.KUCOIN_SANDBOX_API_PASSPHRASE
        else:
            self._base_url = ''
            self._wss_url = ''
            self._api_key = ''
            self._secret_key = ''

    def _request(self, method, uri, timeout=5, auth=True, params=None):
        uri_path = uri
        data_json = ''
        if method in ['GET', 'DELETE']:
            if params:
                strl = []
                for key in sorted(params):
                    strl.append("{}={}".format(key, params[key]))
                data_json += '&'.join(strl)
                uri += '?' + data_json
                uri_path = uri
        else:
            if params:
                data_json = json.dumps(params)
                uri_path = uri + data_json

        headers = {}
        if auth:
            now_time = int(time.time()) * 1000
            str_to_sign = str(now_time) + method + uri_path
            sign = base64.b64encode(
                hmac.new(self._secret_key.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
 
            
            passphrase = base64.b64encode(
                    hmac.new(self._secret_key.encode('utf-8'), self._passphrase_key.encode('utf-8'), hashlib.sha256).digest())
            headers = {
                "KC-API-SIGN": sign,
                "KC-API-TIMESTAMP": str(now_time),
                "KC-API-KEY": self._api_key,
                "KC-API-PASSPHRASE": passphrase,
                "Content-Type": "application/json",
                "KC-API-KEY-VERSION": "2"
                }

        url = self._base_url + uri

        if method in ['GET', 'DELETE']:
            response_data = requests.request(method, url, headers=headers, timeout=timeout)
        else:
            response_data = requests.request(method, url, headers=headers, data=data_json, timeout=timeout)
        if response_data.status_code == 200:
            try:
                data = response_data.json()
            except ValueError:
                raise Exception(response_data.content)
            else:
                if data and data.get('code'):
                    if data.get('code') == '200000':
                        if data.get('data'):
                            return data['data']
                        else:
                            return data
                    else:
                        raise Exception("{}-{}".format(response_data.status_code, response_data.text))
        else:
            raise Exception("{}-{}".format(response_data.status_code, response_data.text))
            
     

    def get_contracts(self):
        contracts = self._request('GET', '/api/v1/symbols')
         

        return contracts

    def get_balances(self):

        balances = self._request('GET', '/api/v1/accounts')
        return balances

    def place_order(self, symbol, side, clientOid, size):
        params = {
            'symbol': symbol,
            'side': side,
            'type': "market",
            'clientOid': clientOid,
            'size': size
                
        }

        order = self._request('POST', '/api/v1/orders', params=params)
        
        return order
        
    def get_all_orders(self):
        params = {
            'tradeType': 'TRADE'
                }
                
        orders = self._request('GET', '/api/v1/orders')

        return orders
    
#kucoin = KucoinClient(True)
# print(kucoin.get_contracts())
# print(kucoin.place_order("BTC-USDT", "buy", "123456ETR001", 1)) 
#print(kucoin.get_all_orders()) 
    
