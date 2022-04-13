import json
import requests
import hmac
import hashlib
import time


class CryptoClient:
    def __init__(self, testnet):
        
        if testnet:
            self._BASE_URL="https://uat-api.3ona.co/v2/"
        else:    
            self._BASE_URL="https://api.crypto.com/v2/"
            
        self._API_KEY = ""
        self._SECRET_KEY = ""
        
        
        with open('keys.json') as keys:
            information = json.load(keys)
            self._API_KEY = information['api_key']
            self._SECRET_KEY = information['secret_key']
            
    
    def get_instruments(self):
        response = requests.get(self._BASE_URL + "public/get-instruments")
        return response.json()
    
    def get_balances(self):
    
        req = {
            "id": 14,
            "method": "private/get-account-summary",
            "api_key": self._API_KEY,
            "params": {},
            "nonce": int(time.time() * 1000)
            }

        # First ensure the params are alphabetically sorted by key
        param_str = ""
        
        if "params" in req:
            for key in req['params']:
                param_str += key
                param_str += str(req['params'][key])
        
        
        payload_str = req['method'] + str(req['id']) + req['api_key'] + param_str + str(req['nonce'])

        req['sig'] = hmac.new(bytes(str(self._SECRET_KEY), 'utf-8'),msg=bytes(payload_str, 'utf-8'),digestmod=hashlib.sha256).hexdigest()
        
        balances = requests.post(self._BASE_URL + "private/get-account-summary", json=req, headers={'Content-Type':'application/json'})
        
        return balances.json()
        
        
        
            
# crypto = CryptoClient(False)
# print(crypto.get_balances())            
            
            
        
        
