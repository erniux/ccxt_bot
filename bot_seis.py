from binance_client import BinanceClient
from bitmex_client import BitmexClient
from kucoin_client import KucoinClient
import pandas as pd
import warnings
import schedule
from datetime import datetime
import time
import secrets
import requests
from enums import *


# TEST
crypto_url = 'https://uat-api.3ona.co'             # https://exchange-docs.crypto.com/spot/index.html
gemini_url = 'https://api.sandbox.gemini.com'      # https://docs.gemini.com/rest-api/
kucoin_url = 'https://openapi-sandbox.kucoin.com'  # https://docs.kucoin.com/ 
binance_url = 'https://testnet.binance.vision'     # https://binance-docs.github.io/apidocs/spot/en/
bitmex_url = 'https://testnet.bitmex.com'          # https://www.bitmex.com/api/explorer/


"""
# PROD
crypto_url = 'https://api.crypto.com'             # https://exchange-docs.crypto.com/spot/index.html
gemini_url = 'https://api.gemini.com'      # https://docs.gemini.com/rest-api/
kucoin_url = 'https://api.kucoin.com'  # https://docs.kucoin.com/ 
binance_url = 'https://api.binance.com'     # https://binance-docs.github.io/apidocs/spot/en/
bitmex_url = 'https://www.bitmex.com/api/v1' # https://www.bitmex.com/api/explorer/co
"""

binance = BinanceClient(True)
TRADE_SYMBOL ="BNBBTC"
TRADE_QUANTITY = 20

pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')
    
in_position = False

def tr(df):
	df['previous_close'] = df['close'].shift(1)
	df['high-low'] = df['high'] - df['low']
	df['high-previous-close'] = abs(df['high'] - df['previous_close'])
	df['low-previous-close'] = abs(df['low'] - df['previous_close'])
	tr = df[['high-low', 'high-previous-close', 'low-previous-close']].max(axis=1)
	
	return tr

def atr(df, period=14):
	# print("calculate the average true range")
	df['tr'] = tr(df)
	
	the_atr = df['tr'].rolling(period).mean()
	
	return the_atr
	

def supertrend(df, period=7, multiplier=3):
	# print("calculating supertrend")
	df['atr'] = atr(df, period)
	df['upperband'] = ((df['high'] + df['low']) / 2) + (multiplier * df['atr'])
	df['lowerband'] = ((df['high'] + df['low']) / 2) - (multiplier * df['atr'])
	df['in_uptrend'] = True

	for current in range(1, len(df.index)):
		previous = current -1
		
		if df['close'][current] > df['upperband'][previous]:
			df['in_uptrend'][current] = True
		elif df['close'][current] < df['lowerband'][previous]:
			df['in_uptrend'][current] = False
		else:
			df['in_uptrend'][current] = df['in_uptrend'][previous]
			
			if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
				df['lowerband'][current] = df['lowerband'][previous]
				
			if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
				df['upperband'][current] = df['upperband'][previous]		
	
	return df

def get_exchanges_to_trade(side):
	arbitrage = get_tickers()
	
	df_ex = pd.DataFrame(arbitrage, columns=['exchange', 'timestamp', 'bid', 'ask'])
	
	if side == SIDE_BUY:
		return df_ex[df_ex['ask']==df_ex['ask'].min()]
	else:
		return df_ex[df_ex['bid']==df_ex['bid'].max()]
		

def check_buy_sell_signals(df):
	global in_position
	
	# print("checking for buy & sells")
	# balances = binance.get_balances()
		
	# print(df.tail(5))	
	last_row_index = len(df.index) - 1
	previous_row_index = last_row_index - 1
	
	# Tests for BUY & SELL force values in the dataframe
	df['in_uptrend'][last_row_index] = False
	df['in_uptrend'][previous_row_index] = True
	in_positon = True
	# end tests
	
	if not df['in_uptrend'][previous_row_index] and	df['in_uptrend'][last_row_index]:   # cambia de false a true
		print("YOU MUST BUY!!!! CHANGED TO UPTREND, BUY")
		if not in_position:
			exchange_buy = get_exchanges_to_trade(SIDE_BUY)
			print(f"TOY EN CHEC BUY AND SELL {exchange_buy}")
			print("AQUI ENIO MI ORDEN DE COMPRA")
			
			in_position = True
		else:
			print("already in position, nothing to do")
		
		
	if df['in_uptrend'][previous_row_index] and	not df['in_uptrend'][last_row_index]:   # cambia de true  a false
		print("YOU MUST SELL!!!! CHANGED TO DOWNTREND, SELL")	
		in_position = True
		if in_position:
			exchange_sell = get_exchanges_to_trade(SIDE_SELL)
			exchange = exchange_sell.iloc[0, :]['exchange']
			order = order(exchange, TRADE_SYMBOL, SIDE_SELL, TRADE_QUANTITY, ORDER_TYPE_MARKET)
			print("AQUI ENVIO MI ORDER DE VENTA")
			
			in_position = False
		else:
			print("you do not have position to sell, nothing to do")
			
def order(exchange, symbol, side, quantity, type):
	if exchange == 'gemini':
	if exchange == 'binance':
		order = binance.place_order(symbol, side, quantity, type)
		print(order)
	elif exchange == 'crypto':
		
	elif exchange == 'bitmex':
		order = bitmex.place_order(symbol, type, quantity, side) # ('XBTUSD', 'Market', 100, 'Buy'))
	elif exchange == 'kucoin':
		order = kucoin.place_order(symbol, type, "", quantity)) 
	
	
				
def get_tickers():
	
	arbitrage = []
	response = requests.get(gemini_url + "/v1/pubticker/btcusd")
	ticker_gemini = response.json()
	gemini = ["gemini", ticker_gemini['volume']['timestamp'], float(ticker_gemini['bid']), float(ticker_gemini['ask'])]
	arbitrage.append(gemini)
	# print(f"GEMINI:: {ticker_gemini['volume']['timestamp']} bid:: {ticker_gemini['bid']} :: ask:: {ticker_gemini['ask']}")  

	data = dict()
	data['instrument_name'] = "BTC_USDT"
	response = requests.get(crypto_url + "/v2/public/get-ticker", params=data)
	ticker_crypto = response.json()['result']['data']
	crypto = ["crypto", ticker_crypto['t'], float(ticker_crypto['b']), float(ticker_crypto['k'])]
	arbitrage.append(crypto)
	# print(f"CRYPTO:: {ticker_crypto['t']}::: bid:: {ticker_crypto['b']} :: ask:: {ticker_crypto['k']}")
	

	data = dict()
	data['symbol'] = "BTC-USDT"
	response = requests.get(kucoin_url + "/api/v1/market/orderbook/level1", params=data)
	ticker_kucoin = response.json()['data']
	kucoin = ["kucoin", ticker_kucoin['time'], float(ticker_kucoin['bestBid']), float(ticker_kucoin['bestAsk'])] 
	# arbitrage.append(kucoin)
	# print(f"KUCOIN:: {ticker_kucoin['time']}::: bid:: {ticker_kucoin['bestBid']} :: ask:: {ticker_kucoin['bestAsk']}")


	data = dict()
	data['symbol'] = "BTCUSDT"
	response = requests.get(binance_url + "/api/v3/ticker/bookTicker", params=data)
	time_response = requests.get(binance_url + "/api/v3/time")
	time_binance = time_response.json()
	ticker_binance = response.json()
	binance =  ["binance", time_binance['serverTime'], float(ticker_binance['bidPrice']), float(ticker_binance['askPrice'])]
	arbitrage.append(binance)
	# print(f"BINANCE:: {time_binance['serverTime']}::: bid:: {ticker_binance['bidPrice']} :: ask:: {ticker_binance['askPrice']}")
	
	
	data = dict()
	data['symbol'] = "XBTUSD"
	data['depth'] = 25
	response = requests.get(bitmex_url + "/api/v1/instrument", params=data)
	ticker_bitmex = response.json()[0]
	bitmex = ["bitmex", ticker_bitmex['timestamp'], float(ticker_bitmex['bidPrice']), float(ticker_bitmex['askPrice'])]
	arbitrage.append(bitmex)
	#print(f"BITMEX:: {ticker_bitmex['timestamp']}::: bid:: {ticker_bitmex['bidPrice']} :: ask:: {ticker_bitmex['askPrice']}")
	
	
	
	return arbitrage
	

	
def run_bot():
	# print(f"Fetching new bars for: {datetime.now().isoformat()}")
	bars = binance.get_historical_candles(TRADE_SYMBOL, KLINE_INTERVAL_1MINUTE, limit=100)
	df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume' ])
	df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms') 
	supertrend_data = supertrend(df)
	
	check_buy_sell_signals(supertrend_data)


run_bot()
# schedule.every(0).seconds.do(run_bot)

# while True:
# 	schedule.run_pending()	
# 	time.sleep(1)
 
