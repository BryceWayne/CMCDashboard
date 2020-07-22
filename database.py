#database.py
import pickle, os
from time import strftime
from pprint import pprint


class database:
	def __init__(self, name):
		self.name = name
		cwd = os.getcwd()
		path = os.path.join(cwd,'data')
		try:
			with open(f'{path}/{self.name}.pkl', 'rb') as f:
				data = pickle.load(f)
			print('Data loaded')
		except:
			data = {}
			if os.path.isdir(path) == False:
				os.makedirs(path)
			with open(f'{path}/{self.name}.pkl', 'wb') as f:
				pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
			print('Data created')
			data['History'] = []
			data['get_coins_markets'] = []
		self.data = data
	def save(self):
		cwd = os.getcwd()
		path = os.path.join(cwd,'data')
		with open(f'{path}/{self.name}.pkl', 'wb') as f:
			pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)
		print("Data saved\n")
	def update(self, timestamp, data):
		entry = {'timestamp':timestamp, 'data':data}
		self.data['get_coins_markets'].append(entry)
		# print("New entry inserted into database")
	def history(self, timestamp, data):
		candle = {'timestamp':timestamp}
		for datum in data:
			candle[datum['symbol'].upper()] = datum['current_price']
		self.data['History'].append(candle)
		

if __name__ == '__main__':
	print("Check.")
	from pycoingecko import CoinGeckoAPI
	from datetime import datetime
	import time
	cg = CoinGeckoAPI()
	db = database('test')
	while True:
		now = datetime.now()
		now = str(now).split('.')[0]
		try:
			print("Timestamp:", now, cg.ping())
			coins_list = cg.get_coins_markets(vs_currency='usd')
			db.update(now, coins_list)
			db.history(now, coins_list)
			db.save()
		except:
			print("Timestamp:", now, "!!!!!!!!!!!Error!!!!!!!!!!")
			pass
		time.sleep(60)
