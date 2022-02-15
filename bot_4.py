import ccxt
import pprint

def run():
	arbitrage()
	initialize()
	
		
def arbitrage():
	#create Triangular Arbitrage Function
	print("Arbitrage Function Running")
	coins = ['BTC', 'LTC', 'ETH']
	
	for exchange in ccxt.exchanges:
		id = exchange
		exch = eval ('ccxt.%s ()' % id)
		markets = exch.load_markets()
		for m in markets:
			if m in coins:
				print(id, m)
			


def initialize():
	pass
	
def active_trader():
	pass


run()
