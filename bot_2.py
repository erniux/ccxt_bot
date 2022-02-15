import websocket
import json
import pprint
import ta
import schedule
from ta.volatility import BollingerBands, AverageTrueRange
import pandas as pd

import secrets
from enums import *

from binance_client import BinanceClient


SOCKET = 'wss://testnet.binance.vision/ws/btcusdt@kline_1m'

binance = BinanceClient(True)


def on_open(ws):
    print('opened connection new version')


def on_close(ws):
    print('connection closed')


def on_error(ws, error):
    print(error)


def on_message(ws, message):
    json_message = json.loads(message)

    candle = json_message['k']

    print(candle)


bars = binance.get_historical_candles("ETHUSDT", KLINE_INTERVAL_1MINUTE, limit=50)

df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume' ])

bb_indicator = BollingerBands(df['close'])

df['upper_band'] = bb_indicator.bollinger_hband()
df['lower_band'] = bb_indicator.bollinger_lband()
df['moving_average'] = bb_indicator.bollinger_mavg()



atr_indicator = AverageTrueRange(df['high'], df['low'], df['close'])

df['atr'] = atr_indicator.average_true_range()
print(df)

# ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_error=on_error, on_message=on_message)
# ws.run_forever()

