#database.py
import pickle, os
from time import strftime
from pprint import pprint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from tqdm import tqdm


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
	def generate(self):
		COLOR = '#f6546a'
		PHI = 0.618
		WINDOW = 120
		history = self.data['History']
		df = pd.DataFrame(history)
		tickers = df.columns.tolist()
		mcap = list(range(1,len(tickers) + 1))
		for _ in ['timestamp']:
			tickers.remove(_)
		INDEX = df.timestamp.tolist()
		print("Generating images.")
		for _, ticker in tqdm(enumerate(tickers)):
			coin = df[['timestamp', ticker]].copy()
			coin[f'SMA_{WINDOW}'] = coin[ticker].rolling(window=WINDOW).mean()
			coin[f'EMA_{WINDOW}'] = coin[ticker].ewm(span=WINDOW).mean()
			mean, sd = np.round(coin[ticker].mean(), 4), np.round(coin[ticker].std(), 4)

			y = df[ticker].tolist()
			X = df['timestamp'].tolist()
			X = np.array(list(range(len(X)))).astype(int)
			X = sm.add_constant(X)
			est = sm.OLS(y, X)
			est = est.fit()
			ts = df.timestamp.tolist()
			ts = np.array(list(range(len(ts)))).astype(int)
			X_prime = np.linspace(ts[0], ts[-1], 100)[:, np.newaxis]
			X_prime = sm.add_constant(X_prime)

			y_hat = est.predict(X_prime)
			slope = np.round((y_hat[-1]-y_hat[0])/(ts[-1]-ts[0]), 6)

			ax = coin.plot(figsize=(16,10), rot=90, title=f'Ticker: {ticker}\nSlope: {slope}, Mean: {mean}, SD: {sd}')
			plt.plot(X_prime[:, 1], y_hat, color=COLOR, alpha=0.618, label='Linear')
			plt.hlines(mean, ts[0], ts[-1], alpha=PHI, linestyle='dashed')
			ax.annotate('Mean', xy=(ts[0], mean), xytext=(ts[0], mean))
			for i in range(1, 7):
				plt.hlines(mean-i*sd, ts[0], ts[-1], alpha=PHI/i, linestyle='dotted')
				plt.hlines(mean+i*sd, ts[0], ts[-1], alpha=PHI/i, linestyle='dotted')
				ax.annotate(f'+{i} SD', xy=(ts[0], mean+sd), xytext=(ts[0], mean+i*sd))
				ax.annotate(f'-{i} SD', xy=(ts[0], mean-sd), xytext=(ts[0], mean-i*sd))
			coin.index = list(range(len(coin)))
			plt.plot(coin[ticker].idxmax(), coin[ticker].max(), 'o', color=COLOR)
			plt.plot(coin[ticker].idxmin(), coin[ticker].min(), 'o', color=COLOR)
			plt.xlim(ts[0]-5/PHI, (1+0.001*5/PHI)*ts[-1])
			plt.xticks(ts[::len(INDEX)//5], INDEX[::len(INDEX)//5], rotation=90)
			plt.legend(loc=4)
			plt.tight_layout()
			plt.savefig(f'./data/pics/{ticker}.png', bbox_inches='tight')
			# plt.show()
			plt.close()
		print("Done generating plots.")

		

if __name__ == '__main__':
	from pycoingecko import CoinGeckoAPI
	from datetime import datetime
	import time
	cg = CoinGeckoAPI()
	db = database('test')
	while True:
		start = datetime.now()
		now = datetime.now()
		now = str(now).split('.')[0]
		try:
			print("Timestamp:", now, cg.ping())
			coins_list = cg.get_coins_markets(vs_currency='usd')
			db.history(now, coins_list)
			db.save()
			db.generate()
		except:
			print("Timestamp:", now, "!!!!!!!!!!!Error!!!!!!!!!!")
			pass
		end = datetime.now()
		dt = (end-start).total_seconds()
		if 60 - dt > 0:
			print(f"Waiting {np.round(60 - dt, 0)} seconds.")
			time.sleep(60 - dt)

