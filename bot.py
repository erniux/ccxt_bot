import websocket
import json
import pprint
import talib
import numpy
import secrets_1
from enums import *
from twilio.rest import Client
from binance_client import BinanceClient


SOCKET = 'wss://testnet.binance.vision/ws/btcusdt@kline_1m'
closes = []
binance = BinanceClient(True)
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BNBBTC'
TRADE_QUANTITY = 0.01 # binance.get_position(TRADE_SYMBOL) # 0.05

if TRADE_QUANTITY > 0:
    in_position = True
else:
    in_position = False
    
    
in_position = False


def send_message(msg):
	account_sid = secrets_1.TWILIO_ACCOUNT_SID
	auth_token = secrets_1.TWILIO_AUTH_TOKEN
	client = Client(account_sid, auth_token) 
 
	message = client.messages.create( 
                              from_='whatsapp:+14155238886',  
                              body= msg,
                              to='whatsapp:+5214427505679' 
                          ) 
     

def on_open(ws):
    print('opened connection new version')


def on_close(ws):
    print('connection closed')


def on_error(ws, error):
    print(error)


def on_message(ws, message):
    global in_position
    
    json_message = json.loads(message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    
    close = candle['c']   # Closed price
    
    if is_candle_closed:
        # pprint.pprint(f'candle closed at {close}')
        closes.append(float(close))
        # print("closes: ", closes)
        
        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            #print(f"all rsi calculated so far {rsi}")
            last_rsi = rsi[-1]
            print(f"current rsi is {last_rsi} oversold:: {RSI_OVERSOLD} overbought:: {RSI_OVERBOUGHT}  position?:: {in_position}")
                       
            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("OVERBOUGHT SELL SELL SELL")
                    order = binance.place_order(TRADE_SYMBOL, SIDE_BUY, TRADE_QUANTITY, ORDER_TYPE_MARKET)
                    send_message(f"bot says::: BUYING ORDER {order['fills']}")
                    logger.info(f"buy Order ::: {order}")
                    in_position = False
                else:
                    print("We do not own any. Nothing to do.")
                
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("IT IS oversold, but you already own it, nothing to do.")
                else:
                    print ("OVERSOLD BUY BUY BUY")
                    order = binance.place_order(TRADE_SYMBOL, SIDE_SELL, TRADE_QUANTITY, ORDER_TYPE_MARKET)
                    send_message(f"bot says::: SELLING ORDER {order['fills']}")
                    logger.info(f"buy Order ::: {order}")
                    in_position = True


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_error=on_error, on_message=on_message)
ws.run_forever()
