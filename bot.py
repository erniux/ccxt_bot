import websocket
import json
import pprint
import talib
import numpy
import secrets
from enums import *

from binance_client import BinanceClient


SOCKET = 'wss://testnet.binance.vision/ws/btcusdt@kline_1m'
RSI_PERIOD = 14
RSI_OVERBOUGHT = 50
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BNBBTC'
TRADE_QUANTITY = 0.05

in_position = False
closes = []
binance = BinanceClient(True)


def order(symbol, side, quantity, order_type):
    try:
        order = binance.place_order(symbol, side, quantity, ORDER_TYPE_MARKET)
        print(order)
    except Exception as e:
        print(f"error placing order with values {symbol}, {side}, {quantity}, {order_type} ::: {e.error}")
        return False
    return True
    

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
        pprint.pprint(f'candle closed at {close}')
        closes.append(float(close))
        print("closes: ", closes)
        
        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print(f"all rsi calculated so far {rsi}")
            last_rsi = rsi[-1]
            print(f"current rsi is {last_rsi}")
            print(f"oversold:: {RSI_OVERSOLD}")
            print(f"overbought:: {RSI_OVERBOUGHT}")
            print(f"position?:: {in_position}")
                       
            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("OVERBOUGHT SELL SELL SELL")
                    order_succeeded = order(
                    TRADE_SYMBOL, SIDE_SELL, 
                    TRADE_QUANTITY, 
                    ORDER_TYPE_MARKET)
                    if order_succeeded:
                        in_position = False
                else:
                    print("We do not own any. Nothing to do.")
                
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("IT IS oversold, but you already own it, nothing to do.")
                else:
                    print ("OVERSOLD BUY BUY BUY")
                    order_succeeded = order(TRADE_SYMBOL, SIDE_BUY, TRADE_QUANTITY, ORDER_TYPE_MARKET)
                    if order_succeeded:
                        in_position = True


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_error=on_error, on_message=on_message)
ws.run_forever()
