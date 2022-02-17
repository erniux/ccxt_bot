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


class GeminiClient:
	def __init__(self, testnet):
		if testnet:
			self._base_url = secrets.GEMINI_SANDBOX_REST_URL
			self._api_key = secrets.GEMINI_SANDBOX_API_KEY
			self._secret_key = secrets.GEMINI_SANDBOX_SECRET_KEY
		else:
			self._base_url = secrets.GEMINI_REST_URL
			self._api_key = secrets.GEMINI_API_KEY
			self._secret_key = secrets.GEMINI_SECRET_KEY
			
			
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
		payload_nonce = str(int(time.mktime(t.timetuple())*1000))
		payload =  {
			"request": "/v1/mytrades", 
			"nonce": payload_nonce
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
		
			
		
gemini = GeminiClient(True)
gemini.get_balances()

