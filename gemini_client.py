import logging
import requests
import secrets_1
import json
from urllib.parse import urlencode
import hmac
import hashlib
import time
import datetime
import base64


logger = logging.getLogger()


class GeminiClient:
	def __init__(self, testnet):
		if testnet:
			self._base_url = secrets_1.GEMINI_SANDBOX_REST_URL
			self._api_key = secrets_1.GEMINI_SANDBOX_API_KEY
			self._secret_key = secrets_1.GEMINI_SANDBOX_SECRET_KEY
		else:
			self._base_url = secrets_1.GEMINI_REST_URL
			self._api_key = secrets_1.GEMINI_API_KEY
			self._secret_key = secrets_1.GEMINI_SECRET_KEY
			
			
	def get_symbols(self):
		
		response = requests.get(self._base_url + "/v1/symbols")
		symbols = response.json()
		
		for s in symbols:
			response = requests.get(self._base_url + "/v1/symbols/details/" + str(s))
			symbol_detail = response.json()
	
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
		#print(my_trades)
		
	def place_order(self, symbol, side, quantity, order_type, price=None):
		
		url = self._base_url + "/v1/order/new"
		gemini_api_key = self._api_key
		gemini_api_secret = self._secret_key.encode()

		t = datetime.datetime.now()
		payload_nonce =  str(int(time.mktime(t.timetuple())*3000))

		payload = {
			"request": "/v1/order/new",
			"nonce": payload_nonce,
			"account": "primary",
			"symbol": symbol,
			"amount": quantity,
			"price": "3633.00",
			"side": side,
			"type": order_type,
			"options": ['immediate-or-cancel'] 
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
		#print(new_order)
	
	def orders_status(self):
		url = self._base_url + "/v1/orders"
		gemini_api_key = self._api_key
		gemini_api_secret = self._secret_key.encode()

		t = datetime.datetime.now()
		payload_nonce =  str(int(time.mktime(t.timetuple())*4000))
		payload =  {
			"request": "/v1/orders", 
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
	
		my_orders = response.json()
		#print(my_orders)
		
	def cancel_order(self, order_id):
		url = self._base_url + "/v1/order/cancel"
		gemini_api_key = self._api_key
		gemini_api_secret = self._secret_key.encode()

		t = datetime.datetime.now()
		payload_nonce =  str(int(time.mktime(t.timetuple())*4000))

		payload = {
			"request": "/v1/order/cancel",
			"nonce": payload_nonce,
			"account": "primary",
			"order_id": order_id
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


		order_cancel = response.json()
		#print(order_cancel)
		

	def get_past_trades(self, symbol):
		url = self._base_url + "/v1/mytrades"
		gemini_api_key = self._api_key
		gemini_api_secret = self._secret_key.encode()

		t = datetime.datetime.now()
		payload_nonce =  str(int(time.mktime(t.timetuple())*4000))
		payload =  {
			
				"nonce": payload_nonce,
				"request": "/v1/mytrades",
				"symbol": symbol,
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
		#print(my_trades)

			
		
#gemini = GeminiClient(True)
#gemini.get_balances()
#gemini.place_order('btcusd','buy',1, 'exchange limit')
#gemini.orders_status()
#gemini.get_past_trades()
#gemini.cancel_order(1714872733)

