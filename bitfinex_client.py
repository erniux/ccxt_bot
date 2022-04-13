import logging
import requests
import secrets
import json
from urllib.parse import urlencode
import hmac
import hashlib
import time
import datetime
import base64


logger = logging.getLogger()


class BitfinexClient:
	def __init__(self, testnet):
		if testnet:
			self._base_public_url = secrets.BITFINEX_SA_PUBLIC_URL
			self._base_private_url = secrets.BITFINEX_SA_PRIVATE_URL
			self._api_key = secrets.BITFINEX_SA_API_KEY
			self._secret_key = secrets.BITFINEX_SA_SECRET_KEY
		else:
			self._base_public_url = secrets.BITFINEX_SA_PUBLIC_URL
			self._base_private_url = secrets.BITFINEX_SA_PRIVATE_URL
			self._api_key = ''
			self._secret_key = ''
			
			
	def get_symbols(self):
		
		response = requests.get(self._base_public_url + "/v2/conf/pub:list:pair:exchange") 
		symbols = response.json()
		
		print(symbols)
	
	def get_balances(self):
		
		url = self._base_url + "/v1/balances"
		gemini_api_key = self._api_key
		gemini_api_secret = self._secret_key.encode()

		t = datetime.datetime.now()
		payload_nonce =  str(int(time.mktime(t.timetuple())*1000))
		payload =  {
			"request": "/v1/balances", 
			"nonce": payload_nonce,
			"account": "primary"
			}
		encoded_payload = json.dumps(payload).encode()
		b64 = base64.b64encode(encoded_payload)
		signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

		request_headers = {
			'Content-Type': "text/plain",
			'Content-Length': "0",
			'X-GEMINI-APIKEY': gemini_api_key,
			'X-GEMINI-PAYLOAD': b64,
			'X-GEMINI-SIGNATURE': signature,
			'Cache-Control': "no-cache"
			}

		response = requests.post(url, headers=request_headers)
	
		my_trades = response.json()
		print(my_trades)
		
	def place_order(self, symbol, side, quantity, order_type, price=None):
		
		endpoint = "/v1/order/new"
		url = base_url + endpoint

		gemini_api_key = "mykey"
		gemini_api_secret = "1234abcd".encode()

		t = datetime.datetime.now()
		payload_nonce =  str(int(time.mktime(t.timetuple())*1000))

		payload = {
			"request": "/v1/order/new",
			"nonce": payload_nonce,
			"symbol": symbol,
			"amount": quantity,
			"price": price,
			"side": "buy",
			"type": "exchange limit",
			"options": ["maker-or-cancel"] 
		}

		encoded_payload = json.dumps(payload).encode()
		b64 = base64.b64encode(encoded_payload)
		signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

		request_headers = { 'Content-Type': "text/plain",
						'Content-Length': "0",
						'X-GEMINI-APIKEY': gemini_api_key,
						'X-GEMINI-PAYLOAD': b64,
						'X-GEMINI-SIGNATURE': signature,
						'Cache-Control': "no-cache" }

		response = requests.post(url,
								data=None,
								headers=request_headers)


		new_order = response.json()
		print(new_order)
		
			
		


