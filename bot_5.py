import ccxt
import schedule
import pandas as pd
import warnings
from datetime import datetime
import time
import secrets
from enums import *
import requests, json

"""
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
bitmex_url = 'https://www.bitmex.com' # https://www.bitmex.com/api/explorer/



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
	print(f"BITMEX:: {ticker_bitmex['timestamp']}::: bid:: {ticker_bitmex['bidPrice']} :: ask:: {ticker_bitmex['askPrice']}")
	

	
	
	return arbitrage
	


def get_last_closed_candle():
	response = requests.get(gemini_url + "/v2/candles/btcusd/1m")
	candles_gemini = response.json()

	data = dict()
	data['instrument_name'] = "BTC_USDT"
	data['timeframe'] = "1m"
	response = requests.get(crypto_url + "/v2/public/get-candlestick", params=data)
	candles_crypto = response.json()
	

	data = dict()
	data['symbol'] = "BTC-USDT"
	data['type'] = "1min"
	response = requests.get(kucoin_url + "/api/v1/market/candles", params=data)
	candles_kucoin = response.json()
	


	data = dict()
	data['symbol'] = "BTCUSDT"
	data['interval'] = "1m"
	response = requests.get(binance_url + "/api/v3/klines", params=data)
	candles_binance = response.json()
	
	print(f"GEMINI::: {candles_gemini[-1]}")
	print(f"CRYPTO::: {candles_crypto['result']['data'][-1]}")
	print(f"KUCOIN::: {candles_kucoin['data'][-1]}")
	print(f"BINANCE::: {candles_binance[-1]}")




def run_bot():
	arbitrage = get_tickers()
	
	df = pd.DataFrame(arbitrage, columns=['exchange', 'timestamp', 'bid', 'ask'])
	print(df)
	
	print(f"comprar :::")
	print(f"{df[df['ask']==df['ask'].min()]}")  
	print(f"vender :::")
	print(f"{df[df['bid']==df['bid'].max()]}")  
	
	

run_bot()
# schedule.every(30).seconds.do(run_bot)
"""

while True:
	schedule.run_pending()	
	time.sleep(1)
"""	

