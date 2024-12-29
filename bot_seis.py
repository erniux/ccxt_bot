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
import requests
from enums import *
import logging
import sys


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


"""
# TEST
crypto_url = 'https://uat-api.3ona.co'             # https://exchange-docs.crypto.com/spot/index.html
gemini_url = 'https://api.sandbox.gemini.com'      # https://docs.gemini.com/rest-api/
kucoin_url = 'https://openapi-sandbox.kucoin.com'  # https://docs.kucoin.com/ 
binance_url = 'https://testnet.binance.vision'     # https://binance-docs.github.io/apidocs/spot/en/
bitfinex_url = 'https://testnet.bitmex.com'          # https://www.bitmex.com/api/explorer/


"""
# PROD
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
    
in_position = False
 
def tr(df): #true range
	df['previous_close'] = df['close'].shift(1)
	df['high-low'] = df['high'] - df['low']
	df['high-previous-close'] = abs(df['high'] - df['previous_close'])
	df['low-previous-close'] = abs(df['low'] - df['previous_close'])
	tr = df[['high-low', 'high-previous-close', 'low-previous-close']].max(axis=1)
	
	return tr

def atr(df, period=14): #average true range
	# print("calculate the average true range")
	df['tr'] = tr(df)
	
	the_atr = df['tr'].rolling(period).mean()
	
	return the_atr
	

def supertrend(df, period=5, multiplier=3.5):
	#print("calculating supertrend")
	hl2 = (df['high'] + df['low']) / 2
	df['atr'] = atr(df, period)
	df['upperband'] = hl2 + (multiplier * df['atr'])
	df['lowerband'] = hl2 - (multiplier * df['atr'])
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

in_position = False

def get_exchanges_to_trade(side):
	arbitrage = get_tickers()
	
	df_ex = pd.DataFrame(arbitrage, columns=['exchange', 'timestamp', 'bid', 'ask'])
	#logger.info(df_ex)
	if side == SIDE_BUY:
		return df_ex[df_ex['ask']==df_ex['ask'].min()]
	else:
		return df_ex[df_ex['bid']==df_ex['bid'].max()]
		

def check_buy_sell_signals(df):
	global in_position
	
	#logger.info("checking for buy & sells")	
	#logger.info(df.tail(5))	
	
	last_row_index = len(df.index) - 1
	previous_row_index = last_row_index - 1

	
	if not df['in_uptrend'][previous_row_index] and	df['in_uptrend'][last_row_index]:   # cambia de false a true
		#logger.info("YOU MUST BUY!!!! CHANGED TO UPTREND, BUY")
		if not in_position:
			exchange_buy = get_exchanges_to_trade(SIDE_BUY)
			exchange = exchange_buy.iloc[0, :]['exchange']
			price = exchange_buy.iloc[0, :]['ask']
			msg = f"ORDEN DE VENTA ::: {exchange} :: PRECIO {price}"
			logger.info(msg)
			in_position = True
		#else:
		#	logger.info("already in position, nothing to do")
		
		
	if df['in_uptrend'][previous_row_index] and	not df['in_uptrend'][last_row_index]:   # cambia de true  a false
		#logger.info("YOU MUST SELL!!!! CHANGED TO DOWNTREND, SELL")	
		if in_position:
			exchange_sell = get_exchanges_to_trade(SIDE_SELL)
			exchange = exchange_sell.iloc[0, :]['exchange']
			price = exchange_sell.iloc[0, :]['bid']
			msg = f"ORDER DE COMPRA ::: {exchange} :: PRECIO {price}"
			logger.info(msg)
			in_position = False
		#else:
		#	print("you do not have position to sell, nothing to do")
		
			
def order(exchange, symbol, side, quantity, type):
	if exchange == 'gemini':
		order = gemini.place_order(symbol, side, quantity, type, price)
	if exchange == 'binance':
		order = binance.place_order(symbol, side, quantity, type)
		print(order)
	elif exchange == 'crypto':
		return
	elif exchange == 'bitmex':
		order = bitfinex.place_order(symbol, type, quantity, side) # ('XBTUSD', 'Market', 100, 'Buy'))
	elif exchange == 'kucoin':
		order = kucoin.place_order(symbol, type, "", quantity)
	
			
def get_tickers():
	
	arbitrage = []

	try: #kukoin
		data = dict()
		symbol_kucoin = f"{TRADE_BASE}{TRADE_QUOTE}"
		data['symbol'] = symbol_kucoin
		response = requests.get(kucoin_url + "/api/v1/market/orderbook/level1", params=data)
		ticker_kucoin = response.json()['data']
		kucoin = ["kucoin", ticker_kucoin['time'], float(ticker_kucoin['bestBid']), float(ticker_kucoin['bestAsk'])] 
		arbitrage.append(kucoin)
		print(f"KUCOIN:: {ticker_kucoin['time']}::: bid:: {ticker_kucoin['bestBid']} :: ask:: {ticker_kucoin['bestAsk']}")
	except Exception:
		logger.error(f"EROR EN REQUEST KUCOIN {response}")

	try:  #binance
		data = dict()
		data['symbol'] = TRADE_SYMBOL
		
		response = requests.get(binance_url + "/api/v3/ticker/bookTicker", params=data)
		time_response = requests.get(binance_url + "/api/v3/time")
		time_binance = time_response.json()
		ticker_binance = response.json()
		binance =  ["binance", time_binance['serverTime'], float(ticker_binance['bidPrice']), float(ticker_binance['askPrice'])]
		arbitrage.append(binance)
		#print(f"BINANCE:: {time_binance['serverTime']}::: bid:: {ticker_binance['bidPrice']} :: ask:: {ticker_binance['askPrice']}")
	except Exception:
		logger.error(f"EROR EN REQUEST BINANCE {response}")
	
	try: #bitfinex
		data = dict()
		
		response = requests.get(bitfinex_url +"/v2/ticker/t" + TRADE_SYMBOL[:-1])
		ticker_bitfinex = (response.json())
		#print(ticker_bitfinex)
		bitfinex =  ["bitfinex", '', float(ticker_bitfinex[2]), float(ticker_bitfinex[6])]
		arbitrage.append(bitfinex)
	except Exception:
		logger.error(f"EROR EN REQUEST BITFINEX {response}")
	
	#logger.info(arbitrage)
	return arbitrage
	

	
def run_bot(base,quote):
	 
	global TRADE_BASE
	global TRADE_QUOTE
	global TRADE_SYMBOL
	
	TRADE_BASE = base #'BTC'
	TRADE_QUOTE = quote #'USDT'
	
	TRADE_SYMBOL = TRADE_BASE + TRADE_QUOTE

	bars = binance.get_historical_candles(TRADE_SYMBOL, KLINE_INTERVAL_1MINUTE, limit=100)
	df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'tipo_candle' ])
	df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms') 
	#print(df) 
	supertrend_data = supertrend(df)
	#print(supertrend_data)
	check_buy_sell_signals(supertrend_data)


#logger.info("Starting bot seis...")
#run_bot()

#schedule.every(1).seconds.do(run_bot(base='BTC',quote='USDT'))

#while True:
#	schedule.run_pending()
#	time.sleep(1)

if __name__ == "__main__":
    # Verificamos que se hayan pasado al menos 2 argumentos
    if len(sys.argv) < 3:
        print("Uso: python mi_script.py <BASE> <QUOTE>")
        sys.exit(1)
    
    # Capturamos los valores de base y quote
    base = sys.argv[1]
    quote = sys.argv[2]
    
    logger.info("Starting bot seis...")
    
    # Programar la ejecución del bot con schedule
    schedule.every(1).seconds.do(run_bot, base=base, quote=quote)

    while True:
        schedule.run_pending()
        time.sleep(1)