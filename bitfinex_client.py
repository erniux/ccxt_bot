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


class BitfinexClient:
	def __init__(self, testnet):
		if testnet:
			self._base_public_url = secrets_1.BITFINEX_SA_PUBLIC_URL
			self._base_private_url = secrets_1.BITFINEX_SA_PRIVATE_URL
			self._api_key = secrets_1.BITFINEX_SA_API_KEY
			self._secret_key = secrets_1.BITFINEX_SA_SECRET_KEY
		else:
			self._base_public_url = secrets_1.BITFINEX_SA_PUBLIC_URL
			self._base_private_url = secrets_1.BITFINEX_SA_PRIVATE_URL
			self._api_key = ''
			self._secret_key = ''
			
			
	def get_symbols(self):
		
		response = requests.get(self._base_public_url + "/v2/conf/pub:list:pair:exchange") 
		symbols = response.json()
		
		print(symbols)
	
	def get_balances(self):
		return
		
		
		
	def place_order(self, symbol, side, quantity, order_type, price=None):
		return
		

		
			
		


