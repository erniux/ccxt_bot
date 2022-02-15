from binance_client import BinanceClient
import pandas as pd
import warnings
import schedule
from datetime import datetime
import time
import secrets
from enums import *

pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')

binance = BinanceClient(True)
trade_symbol = "BNBBTC"


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

	
in_position = False

def check_buy_sell_signals(df):
	global in_position
	
	# print("checking for buy & sells")
	balances = binance.get_balances()
		
	# print(df.tail(5))	
	last_row_index = len(df.index) - 1
	previous_row_index = last_row_index - 1
	
	if not df['in_uptrend'][previous_row_index] and	df['in_uptrend'][last_row_index]:   # cambia de false a true
		print("YOU MUST BUY!!!! CHANGED TO UPTREND, BUY")
		if not in_position:
			order = binance.place_order(trade_symbol, SIDE_BUY, 0.05, ORDER_TYPE_MARKET)
			print(order)
			print(balances)
			in_position = True
		else:
			print("already in position, nothing to do")
		
		
	if df['in_uptrend'][previous_row_index] and	not df['in_uptrend'][last_row_index]:   # cambia de true  a false
		print("YOU MUST SELL!!!! CHANGED TO DOWNTREND, SELL")	
		if in_position:
			order = binance.place_order(trade_symbol, SIDE_SELL, 0.05, ORDER_TYPE_MARKET)
			print(order)
			print(balances)
			in_position = False
		else:
			print("you do not have position to sell, nothing to do")
	
def run_bot():
	# print(f"Fetching new bars for: {datetime.now().isoformat()}")
	bars = binance.get_historical_candles(trade_symbol, KLINE_INTERVAL_1MINUTE, limit=100)
	df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume' ])
	df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms') 
	supertrend_data = supertrend(df)
	
	check_buy_sell_signals(supertrend_data)


schedule.every(1).seconds.do(run_bot)
	

while True:
	schedule.run_pending()	
	time.sleep(1)
 
