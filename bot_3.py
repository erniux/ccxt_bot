from binance_client import BinanceClient
import pandas as pd
import warnings
import schedule
from datetime import datetime
import time
import secrets_1
from enums import *
import logging
from twilio.rest import Client



logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s :: %(message)s")

stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("info.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')

binance = BinanceClient(True)
TRADE_SYMBOL = "BNBBTC"
TRADE_QUANTITY = 0.1 #binance.get_position(TRADE_SYMBOL) # 0.05

print(TRADE_QUANTITY)

in_position = False


def send_message(msg):
	account_sid = secrets_1.TWILIO_ACCOUNT_SID
	auth_token = secrets_1.TWILIO_AUTH_TOKEN
	client = Client(account_sid, auth_token) 
 
	message = client.messages.create( 
                              from_=secrets_1.WA_FROM,  
                              body= msg,
                              to=secrets_1.WA_TO 
                          ) 
 
	

def tr(df):
	df['previous_close'] = df['close'].shift(1)
	df['high-low'] = df['high'] - df['low']
	df['high-previous-close'] = abs(df['high'] - df['previous_close'])
	df['low-previous-close'] = abs(df['low'] - df['previous_close'])
	tr = df[['high-low', 'high-previous-close', 'low-previous-close']].max(axis=1)
	
	return tr

def atr(df, period=5):
	# print("calculate the average true range")
	df['tr'] = tr(df)
	
	the_atr = df['tr'].rolling(period).mean()
	
	return the_atr
	

def supertrend(df, period=5, multiplier=3.5):
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


def check_buy_sell_signals(df):
	global in_position
	
	logger.info("checking for buy & sells")
	balances = binance.get_balances()
		
	logger.info(df.tail(5))
	last_row_index = len(df.index) - 1
	previous_row_index = last_row_index - 1
	logger.info(f"in_uptrend last_row index::: {df['in_uptrend'][previous_row_index]}")
	logger.info(f"in uptrend previous_row_index ::: {df['in_uptrend'][previous_row_index]}")
	logger.info(f"in_position?::: {in_position}")
	
	if not df['in_uptrend'][previous_row_index] and	df['in_uptrend'][last_row_index]:   # cambia de false a true
		if not in_position:
			order = binance.place_order(TRADE_SYMBOL, SIDE_BUY, TRADE_QUANTITY, ORDER_TYPE_MARKET)
			send_message(f"bot_3 says::: BUYING ORDER {order['fills']}")
			logger.info(f"buy Order ::: {order}")
			in_position = True
		else:
			logger.info("NOTHING TO BUY")
		
		
	if df['in_uptrend'][previous_row_index] and	not df['in_uptrend'][last_row_index]:   # cambia de true  a false	
		if in_position:
			order = binance.place_order(TRADE_SYMBOL, SIDE_SELL, TRADE_QUANTITY, ORDER_TYPE_MARKET)
			send_message(f"bot_3 says ::: SELLING ORDER {order['fills']}")
			logger.info(f"sell Order ::: {order}")
			in_position = False
		else:
			logger.info("NOTHING TO SELL")
	
def run_bot():
	# print(f"Fetching new bars for: {datetime.now().isoformat()}")
	bars = binance.get_historical_candles(TRADE_SYMBOL, KLINE_INTERVAL_1MINUTE, limit=100)
	df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume' ])
	df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms') 
	supertrend_data = supertrend(df)
	
	check_buy_sell_signals(supertrend_data)



schedule.every(1).minute.do(run_bot)

while True:
	schedule.run_pending()	
	time.sleep(1)
 
