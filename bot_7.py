from binance_client import BinanceClient
from kucoin_client import KucoinClient
from crypto_client import CryptoClient
from gemini_client import GeminiClient
from bitfinex_client import BitfinexClient
import pandas as pd
import warnings
import schedule
from datetime import datetime
import time
import secrets
import requests
from enums import *
from twilio.rest import Client
import logging


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s :: %(message)s")

stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("bot_seis.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


# PROD
crypto_url = 'https://api.crypto.com'             # https://exchange-docs.crypto.com/spot/index.html
gemini_url = 'https://api.gemini.com'      # https://docs.gemini.com/rest-api/
kucoin_url = 'https://api.kucoin.com'  # https://docs.kucoin.com/ 
binance_url = 'https://api.binance.com'     # https://binance-docs.github.io/apidocs/spot/en/
bitfinex_url = 'https://api-pub.bitfinex.com' # https://www.bitmex.com/api/explorer/co


binance = BinanceClient(True)
crypto = CryptoClient(True)
gemini = GeminiClient(True)
kucoin = KucoinClient(True)
bitfinex = BitfinexClient(True)

TRADE_SYMBOL = ""
TRADE_QUOTE = ""
TRADE_BASE = ""
TRADE_QUANTITY = 20

pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')
    
 

def get_exchanges_to_trade(side):
	arbitrage = get_tickers()
	
	df_ex = pd.DataFrame(arbitrage, columns=['exchange', 'symbol', 'timestamp', 'bid', 'ask'])
	logger.info(df_ex)
	if side == SIDE_BUY:
		return df_ex[df_ex['ask']==df_ex['ask'].min()]
	else:
		return df_ex[df_ex['bid']==df_ex['bid'].max()]
		

def check_buy_sell_signals():
	global in_position
	
	
	exchange_buy = get_exchanges_to_trade(SIDE_BUY)
	exchange_to_buy = exchange_buy.iloc[0, :]['exchange']
	price_to_buy = exchange_buy.iloc[0, :]['ask']
	symbol_to_buy = exchange_buy.iloc[0, :]['symbol']
	msg = f"Compra a ::: {exchange_to_buy} :: PRECIO {price_to_buy} :: {symbol_to_buy}"
	
	logger.info(msg)
	
	order_buy = order(exchange_to_buy, symbol_to_buy, 'buy', 2, price_to_buy)


	exchange_sell = get_exchanges_to_trade(SIDE_SELL)
	exchange_to_sell = exchange_sell.iloc[0, :]['exchange']
	price_to_sell = exchange_sell.iloc[0, :]['bid']
	symbol_to_sell = exchange_sell.iloc[0, :]['symbol']
	msg = f"Venta a ::: {exchange_to_sell} :: PRECIO {price_to_sell} :: {symbol_to_sell}"
	logger.info(msg)
	
	order_buy = order(exchange_to_sell, symbol_to_sell, 'sell', 2, price_to_sell)

			
def order(exchange, symbol, side, quantity, price):
	if exchange == 'gemini':
		order = gemini.place_order(symbol, side, quantity,'exchange limit' ,price)    # symbol, side, quantity, order_type, price=None
	if exchange == 'binance':
		order = binance.place_order(symbol, side, quantity, MARKET)   # symbol, side(BUY),, quantity, order_type (MARKET),
	elif exchange == 'crypto':
		return
	elif exchange == 'bitfinex':
		order = bitmex.place_order(symbol, type, quantity, side) # ('XBTUSD', 'Market', 100, 'Buy'))
	elif exchange == 'kucoin':
		order = kucoin.place_order(symbol, type, "123456ETR001", quantity)  #(kucoin.place_order("BTC-USDT", "buy", "123456ETR001", 1)) 
	
	return order

				
def get_tickers():
	
	arbitrage = []
	try:
		symbol_gemini = TRADE_SYMBOL[:-1].lower()
		response = requests.get(gemini_url + f"/v1/pubticker/{symbol_gemini}")
		ticker_gemini = response.json()
		
		gemini = ["gemini", symbol_gemini, ticker_gemini['volume']['timestamp'], float(ticker_gemini['bid']), float(ticker_gemini['ask'])]
		arbitrage.append(gemini)
		# print(f"GEMINI:: {ticker_gemini['volume']['timestamp']} bid:: {ticker_gemini['bid']} :: ask:: {ticker_gemini['ask']}")  
	except Exception:
		logger.error(f"EROR EN REQUEST GEMINI {response}, {response.url} ")

	try:
		data = dict()
		symbol_crypto = f"{TRADE_BASE}_{TRADE_QUOTE}"
		data['instrument_name'] = symbol_crypto
		response = requests.get(crypto_url + "/v2/public/get-ticker", params=data)
		ticker_crypto = response.json()['result']['data']
		crypto = ["crypto", symbol_crypto, ticker_crypto['t'], float(ticker_crypto['b']), float(ticker_crypto['k'])]
		arbitrage.append(crypto)
		# print(f"CRYPTO:: {ticker_crypto['t']}::: bid:: {ticker_crypto['b']} :: ask:: {ticker_crypto['k']}")
	except Exception:
		logger.error(f"EROR EN REQUEST CRYPTO {response} ")
	

	try:
		data = dict()
		symbol_kucoin = f"{TRADE_BASE}-{TRADE_QUOTE}"
		data['symbol'] = symbol_kucoin
		response = requests.get(kucoin_url + "/api/v1/market/orderbook/level1", params=data)
		ticker_kucoin = response.json()['data']
		kucoin = ["kucoin", symbol_kucoin, ticker_kucoin['time'], float(ticker_kucoin['bestBid']), float(ticker_kucoin['bestAsk'])] 
		arbitrage.append(kucoin)
		# print(f"KUCOIN:: {ticker_kucoin['time']}::: bid:: {ticker_kucoin['bestBid']} :: ask:: {ticker_kucoin['bestAsk']}")
	except Exception:
		logger.error(f"EROR EN REQUEST KUCOIN {response}")

	try:
		data = dict()
		data['symbol'] = TRADE_SYMBOL
		response = requests.get(binance_url + "/api/v3/ticker/bookTicker", params=data)
		time_response = requests.get(binance_url + "/api/v3/time")
		time_binance = time_response.json()
		ticker_binance = response.json()
		binance =  ["binance", TRADE_SYMBOL, time_binance['serverTime'], float(ticker_binance['bidPrice']), float(ticker_binance['askPrice'])]
		arbitrage.append(binance)
		# print(f"BINANCE:: {time_binance['serverTime']}::: bid:: {ticker_binance['bidPrice']} :: ask:: {ticker_binance['askPrice']}")
	except Exception:
		logger.error(f"EROR EN REQUEST BINANCE {response}")
	
	try:
		data = dict()
		data['symbols'] = "t"+ TRADE_SYMBOL
		symbol =  TRADE_SYMBOL[:-1]
		logger.info(symbol)
		response = requests.get(bitfinex_url +"/v2/ticker/t" + symbol)
		ticker_bitfinex = (response.json())
		bitfinex =  ["bitfinex", symbol, '', float(ticker_bitfinex[2]), float(ticker_bitfinex[6])]
		arbitrage.append(bitfinex)
	except Exception:
		logger.error(f"EROR EN REQUEST BITFINEX {response}, {response.url}")
	
	#logger.info(arbitrage)
	return arbitrage
	

	
def run_bot():
	global TRADE_BASE
	global TRADE_QUOTE
	global TRADE_SYMBOL
	
	#print(f"Fetching new bars for: {datetime.now().isoformat()}")
	TRADE_BASE = 'BTC'
	TRADE_QUOTE = 'USDT'
	
	TRADE_SYMBOL = TRADE_BASE + TRADE_QUOTE

	check_buy_sell_signals()


logger.info("Starting bot siete...")
#run_bot()

schedule.every(30).seconds.do(run_bot)

while True:
	schedule.run_pending()
	time.sleep(1)
 
