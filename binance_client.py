import logging
import requests
import secrets
from urllib.parse import urlencode
import hmac
import hashlib
import time


logger = logging.getLogger()


class BinanceClient:
	def __init__(self, testnet):
		if testnet:
			self._base_url = secrets.BINANCE_SPOT_TESTNET_URL
			self._wss_url = secrets.BINANCE_SPOT_TESTNET_WS_URL
			self._api_key = secrets.BINANCE_SPOT_TESTNET_API_KEY
			self._secret_key = secrets.BINANCE_SPOT_TESTNET_SECRET_KEY
		else:
			self._api_key = secrets.BINANCE_SPOT_API_URL
			self._secret_key = secrets.BINANCE_SPOT_SECRET_KEY
			self._base_url = secrets.BINANCE_SPOT_API_URL
			self._wss_url = secrets.BINANCE_SPOT_WS_URL

		self.headers = {'X-MBX-APIKEY': self._api_key}
        
	def _generate_signature(self, data):
		return hmac.new(self._secret_key.encode("utf-8"), urlencode(data).encode("utf-8"), hashlib.sha256).hexdigest()

	def _make_request(self, method, endpoint, data):
		if method == 'GET':
			try:
				response = requests.get(self._base_url + endpoint, params=data, headers=self.headers)
			except Exception as e:
				logger.error(f"Error en conexion al hacer {method} a {endpoint} : {e}")
        
		elif method == 'POST':
			try:
				response = requests.post(self._base_url + endpoint, params=data, headers=self.headers)
			except Exception as e:
				logger.error(f"Error en conexion al hacer {method} a {endpoint} : {e}")
		elif method == 'DELETE':
			try:
				response = requests.delete(self._base_url + endpoint, params=data, headers=self.headers)
			except Exception as e:
				logger.error(f"Error en conexion al hacer {method} a {endpoint} : {e}")
		else:
			raise ValueError()

		if response.status_code == 200:
			return response.json()
		else:
			logger.error("CANT DETERMNE WHAT HAPPENED %s", response.status_code)

	def get_contracts(self):
		exchange_info = self._make_request("GET", "/api/v3/exchangeInfo", None)
		contracts = dict()

		if exchange_info is not None:
			for contract_data in exchange_info['symbols']:
				contracts[contract_data['symbol']] = contract_data

		return contracts
        
        
	def get_historical_candles(self, symbol, interval, limit=1000):
		data = dict()
		data['symbol'] = symbol
		data['interval'] = interval
		data['limit'] = limit
		
		candles = []
		
		raw_candles = self._make_request("GET", "/api/v3/klines", data)
		
		if raw_candles is not None:
			for c in raw_candles:
				candles.append([c[0], float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5])])

		return candles
        
	def get_balances(self):
		data = dict()
		data['timestamp'] = int(time.time() * 1000)
		data['signature'] = self._generate_signature(data)
		account_data = self._make_request("GET", "/api/v3/account", data)
		balances = dict()
		if account_data is not None:
			for a in account_data['balances']:
				balances[a['asset']] = a

		return balances
        
	def place_order(self, symbol, side, quantity, order_type, price=None, tif=None):
		data = dict()
		data['symbol'] = symbol
		data['side'] = side
		data['quantity'] = quantity
		data['type'] = order_type

		if price is not None:
			data['price'] = price

		if tif is not None:
			data['timeInForce'] = tif

		data['timestamp'] = int(time.time() * 1000)
		data['signature'] = self._generate_signature(data)

		order_status = self._make_request("POST", "/api/v3/order", data)


		return order_status

	def get_order_status(self, symbol, order_id):
		data = dict()
		data['orderId'] = order_id
		data['symbol'] = symbol
		data['timestamp'] = int(time.time() * 1000)
		data['signature'] = self._generate_signature(data)

		order_status = self._make_request("GET", "/api/v3/order", data)
		if order_status is not None:
			return order_status

		return order_status

	def get_current_open_orders(self):
		data = dict()
		data['timestamp'] = int(time.time() * 1000)
		data['signature'] = self._generate_signature(data)

		orders_open = self._make_request("GET", "/api/v3/openOrders", data)

		if orders_open is not None:
			return orders_open
			
	def get_all_orders(self, symbol):
		data = dict()
		data['symbol'] = symbol
		data['timestamp'] = int(time.time() * 1000)
		data['signature'] = self._generate_signature(data)

		orders_open = self._make_request("GET", "/api/v3/allOrders", data)

		if orders_open is not None:
			return orders_open
			
	def get_my_trades(self, symbol):
		data = dict()
		data['symbol'] = symbol
		data['timestamp'] = int(time.time() * 1000)
		data['signature'] = self._generate_signature(data)

		my_trades = self._make_request("GET", "/api/v3/myTrades", data)

		if my_trades is not None:
			return my_trades

	def get_position(self, symbol):
		contracts = binance.get_contracts()
		base_asset = contracts['BNBUSDT']['baseAsset']
		balances = binance.get_balances()
		
		position = (float(balances[base_asset]['free']) * 0.01) / 0.50
		
		
		return position

	
# binance = BinanceClient(True)
# print(binance.get_position('BNBBTC'))

# orders = binance.get_my_trades('ETHUSDT')
# for o in orders:
#	order_detail = binance.get_order_status('ETHUSDT',o['orderId'])
#	print(o['symbol'], o['orderId'], o['price'], o['time'])
#	print(order_detail)
	
