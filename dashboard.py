import numpy as np
from bokeh.io import curdoc, output_file
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Range1d, RangeTool, LinearAxis
from bokeh.models.ranges import DataRange1d
from bokeh.models.widgets import Slider, TextInput, Tabs, Panel, Button, DataTable, Div, CheckboxGroup
from bokeh.models.widgets import NumberFormatter, TableColumn, Dropdown, RadioButtonGroup, Select
from bokeh.models.glyphs import VBar
from bokeh.plotting import figure
from bokeh.models import CustomJS, HoverTool, NumeralTickFormatter
from pprint import pprint
import pandas as pd
import requests
import matplotlib.pyplot as plt
import datetime
from sklearn import preprocessing
from pprint import pprint

"""
DEFAULTS
"""
plt.style.use('default')
PHI = 1.618
w = 12*60*60*1000 # half day in ms
WINDOW = 800
"""
SETUP DATA
"""
def get_data(market='Bitcoin'):
	z = datetime.datetime.today()
	z.strftime("%x")
	temp = str(z).split('-')
	current_day = temp[0]+temp[1]+temp[2].split(" ")[0]
	web = requests.get(f"https://coinmarketcap.com/currencies/{market.lower()}/historical-data/?start=20130428&end=" + current_day)
	dfs = pd.read_html(web.text)
	data = dfs[2]
	data = data.iloc[::-1]
	data['Date'] = pd.to_datetime(data['Date'])
	data['Close'] = data['Close**']
	data['Open'] = data['Open*']
	LENGTH = 30
	window1, window2 = LENGTH, 7*LENGTH
	data['Daily MA'] = data['Close'].rolling(window=window1).mean()
	data['Weekly MA'] = data['Close'].rolling(window=window2).mean()
	data['Risk'] = data['Daily MA']/data['Weekly MA']
	min_max_scaler = preprocessing.MinMaxScaler()
	np_scaled = min_max_scaler.fit_transform(data[['Risk']])
	data['Risk'] = np_scaled
	data['Average Risk'] = data['Risk'].mean()
	for _ in range(1, 10):
		data[f"L{_}"] = _/10*np.ones_like(data['Close'])
	data['Scaled'] = data['Close']/data['Close'].max()
	data = RSI(data)
	return data

def RSI(df, n=14):
	prices = df['Close']
	deltas = np.diff(prices)
	seed = deltas[:n+1]
	up = seed[seed >= 0].sum()/n
	down = -seed[seed < 0].sum()/n
	rs = up/down
	rsi = np.zeros_like(prices)
	rsi[:n] = 100-100//(1 + rs)
	for i in range(n, len(prices)):
		delta = deltas[i-1]
		if delta > 0:
			upval = delta
			downval = 0
		else:
			upval = 0
			downval = -delta

		up = (up*(n-1) + upval)/n
		down = (down*(n-1) + downval)/n
		rs = up/down
		rsi[i] = 100-100/(1 + rs)
	df['RSI'] = rsi
	df['RSI30'] = 30*np.ones_like(rsi)
	df['RSI70'] = 70*np.ones_like(rsi)
	return df

df = get_data()
source = ColumnDataSource(df)

"""
SETUP PLOTS
"""
''' INTRO '''
intro = Select(title="Cryptocurrency", value="Bitcoin",
               options=['Bitcoin', 'Ethereum', 'Litecoin', 'Verge', 'Chainlink',
						'Tezos', 'XRP', 'EOS', 'Stellar', 'Cardano', '0x', 'Bitcoin-Cash'])

# ''' PRICE '''
# inc = source.data['Close'] >= source.data['Open']
# dec = source.data['Close'] < source.data['Open']
price = figure(plot_height=int(0.8*WINDOW), plot_width=int(PHI*WINDOW), title=intro.value, tools="xpan, hover", x_axis_type="datetime",
				 y_axis_type="linear", x_range=(source.data['Date'][0], source.data['Date'][-1]),
				 y_range=(min(source.data['Low']), max(source.data['High'])))
price.line(x='Date', y='Close', line_width=1.618, source=source)
price.line(x='Date', y='Daily MA', line_width=1, line_alpha=0.8, line_color='red', legend_label='Daily MA', source=source)
price.line(x='Date', y='Weekly MA', line_width=1, line_alpha=0.6, line_color='green', legend_label='Weekly MA', source=source)
price.xaxis.major_label_orientation = np.pi/4
price.yaxis.axis_label = 'Price'
price.grid.grid_line_alpha=0.3
price_hover = price.select(dict(type=HoverTool))
price_hover.tooltips = [
		("Date", "@Date{%Y-%m-%d}"),
        ("Open", "@Open{%0.00000000f}"),
        ("High", "@High{%0.00000000f}"),
        ("Low", "@Low{%0.00000000f}"),
        ("Close", "@Close{%0.00000000f}"),
        ("Volume", "@Volume{%0.00000000f}"),
        ]
price_hover.formatters = {
        'Date': 'datetime',
        'Open' : 'printf',
        'High' : 'printf',
        'Low' : 'printf',
        'Close' : 'printf',
        'Volume' : 'printf',
    }
# price.segment(x0='Date', y0='High', x1='Date', y1='Low', color="black", source=source)
# price.vbar(x=source.data['Date'][inc], width=w, bottom=source.data['Open'][inc], top=source.data['Close'][inc], fill_color="#00B81B", line_color="black")
# price.vbar(x=source.data['Date'][dec], width=w, top=source.data['Open'][dec], bottom=source.data['Close'][dec], fill_color="#FF3535", line_color="black")

select = figure(title="Drag the middle and edges of the selection box to change the range above",
                plot_height=int(0.2*WINDOW), plot_width=int(PHI*WINDOW), y_range=price.y_range,
                x_axis_type="datetime", y_axis_type=None, x_range=(source.data['Date'][0], source.data['Date'][-1]),
                tools="", toolbar_location=None, background_fill_color="#efefef")

price_range = RangeTool(x_range=price.x_range)
price_range.overlay.fill_color = "navy"
price_range.overlay.fill_alpha = 0.1618

select.line('Date', 'Close', source=source)
select.ygrid.grid_line_color = None
select.add_tools(price_range)
select.toolbar.active_multi = price_range

''' MOVING AVERAGE'''
# ma = figure(plot_height=WINDOW, plot_width=int(PHI*WINDOW), title="Moving Averages", tools="crosshair,pan,reset,save,wheel_zoom", x_axis_type="datetime")
# ma.xaxis.major_label_orientation = np.pi/4
# ma.grid.grid_line_alpha=0.3
# ma.line(x='Date', y="Daily MA", line_width=1, line_alpha=1, source=source, line_color='red', legend_label='Daily MA')
# ma.line(x='Date', y="Weekly MA", line_width=1.618, line_alpha=0.6, source=source, line_color='green', legend_label='Weekly MA')
# ma_period = TextInput(value=str(30), title="Moving Average Period")

''' RSI '''
rsi_plot = figure(plot_height=int(0.8*WINDOW), plot_width=int(PHI*WINDOW), title=intro.value+' Relative Strength Index', tools="xpan", x_axis_type="datetime",
				 y_axis_type="linear", x_range=(source.data['Date'][10], source.data['Date'][-10]),
				 y_range=(0, 100))
rsi_plot.line(x='Date', y='RSI', line_width=1, source=source, legend_label='Relative Strength Index')
rsi_plot.line(x='Date', y='RSI30', line_width=1, source=source, line_color='red', line_dash='dashed', legend_label='Oversold')
rsi_plot.line(x='Date', y='RSI70', line_width=1, source=source, line_color='green', line_dash='dashed', legend_label='Overbought')
rsi_plot.xaxis.major_label_orientation = np.pi/4
rsi_plot.yaxis.axis_label = 'RSI'
rsi_plot.grid.grid_line_alpha=1/PHI

select_rsi = figure(title="Drag the middle and edges of the selection box to change the range above",
                plot_height=int(0.2*WINDOW), plot_width=int(PHI*WINDOW), y_range=rsi_plot.y_range,
                x_axis_type="datetime", y_axis_type=None, x_range=(source.data['Date'][0], source.data['Date'][-1]),
                tools="", toolbar_location=None, background_fill_color="#efefef")

rsi_range = RangeTool(x_range=rsi_plot.x_range)
rsi_range.overlay.fill_color = "navy"
rsi_range.overlay.fill_alpha = 0.1618

select_rsi.line('Date', 'RSI', source=source)
select_rsi.ygrid.grid_line_color = None
select_rsi.add_tools(rsi_range)
select_rsi.toolbar.active_multi = rsi_range

''' RISK '''
risk = figure(plot_height=WINDOW, plot_width=int(PHI*WINDOW), title=intro.value + " Risk", tools="crosshair", x_axis_type="datetime")
risk.xaxis.major_label_orientation = np.pi/4
risk.grid.grid_line_alpha=0.3
risk.line(x='Date', y="Risk", line_width=1, line_alpha=1, source=source, line_color='black', legend_label='Risk')
risk.y_range = Range1d(start=0, end=1)

risk.extra_y_ranges['Price'] = Range1d(start=source.data['Close'].min(), end=source.data['Close'].max())
risk.add_layout(LinearAxis(y_range_name="Price", axis_label='Price ($)'), 'right')
risk.line(x='Date', y='Close', source=source, y_range_name='Price', line_width=1/PHI, color='blue', legend_label='Price')

"""
Setting up widgets
"""

"""
Set up callbacks
"""
def select_crypto(attr, old, new):
	df = get_data(intro.value)
	source.data = df.to_dict('list')
	price.title.text = intro.value
	price.x_range.start = select.x_range.start = source.data['Date'][0]
	price.x_range.end = select.x_range.end = source.data['Date'][-1]
	price.y_range.start = min(source.data['Close**'])
	price.y_range.end = max(source.data['Close**'])
	rsi_plot.title.text = str(intro.value) + ' Relative Strength Index'
	rsi_plot.x_range.start = select_rsi.x_range.start = source.data['Date'][0]
	rsi_plot.x_range.end = select_rsi.x_range.end = source.data['Date'][-1]
	rsi_plot.y_range.start = min(source.data['RSI'])
	rsi_plot.y_range.end = max(source.data['RSI'])
	risk.title.text = str(intro.value) + ' Risk'
	price_hover = price.select(dict(type=HoverTool))
	risk.extra_y_ranges['Price'] = Range1d(start=df['Close'].min(), end=df['Close'].max())
	# inc = source.data['Close'] >= source.data['Open']
	# dec = source.data['Close'] < source.data['Open']
	# price.vbar.x = source.data['Date'][inc]
	# price.vbar.bottom = source.data['Open'][inc]
	# price.vbar.top = source.data['Close'][inc]
	# price.vbar.x = source.data['Date'][dec]
	# price.vbar.bottom = source.data['Open'][dec]
	# price.vbar.top = source.data['Close'][dec]
	
	
intro.on_change('value', select_crypto)

# def update_y_range(attr, new, old):
# 	x_range = (price.x_range.start, price.x_range.end)
# 	current_day = str(datetime.datetime.fromtimestamp((x_range[0])/1E3))
# 	current_day = current_day.split(' ')[0] 
# 	current_day = np.datetime64(current_day)
# 	dates = source.data['Date']
# 	print(current_day)
# 	print(str(dates[0]).split('T')[0])
# 	# first_day = datetime.datetime.strptime(str(dates[0]).strip('.')[0], '%Y-%m-%dT%H:%M:%S')
# 	# print((first_day == current_day))
# 	close = source.data['Close**']
# 	# price.y_range.start = min(close)
# 	# price.y_range.end = max(close)

# price_range.x_range.on_change('start', update_y_range)
# price_range.x_range.on_change('end', update_y_range)

# def change_ma_period(attr, old, new):
# 	df = pd.DataFrame(source.data)
# 	df['Daily MA'] = df['Close**'].rolling(window=int(ma_period.value)).mean()
# 	df['Weekly MA'] = df['Close**'].rolling(window=7*int(ma_period.value)).mean()
# 	df['Risk'] = df['Daily MA']/df['Weekly MA']
# 	min_max_scaler = preprocessing.MinMaxScaler()
# 	np_scaled = min_max_scaler.fit_transform(df[['Risk']])
# 	df['Risk'] = np_scaled
# 	source.data = df.to_dict('list')

# ma_period.on_change('value', change_ma_period)

# Set up layouts and add to document

tab0 = row(intro)
tab0 = Panel(child=tab0, title="Crypto Selection")

tab1 = row(column(price, select), width=int(PHI*400))
tab1 = Panel(child=tab1, title="Price")

# tab2 = row(ma, column(ma_period), width=int(PHI*400))
# tab2 = Panel(child=tab2, title="Moving Averages")
tab2 = row(column(rsi_plot, select_rsi), width=int(PHI*400))
tab2 = Panel(child=tab2, title="RSI")

tab3 = row(risk, width=int(PHI*400))

tab3 = Panel(child=tab3, title="Risk")

tabs = Tabs(tabs=[tab0, tab1, tab2, tab3])

curdoc().title = "CMC Dashboard"
curdoc().theme = 'caliber'
curdoc().add_root(tabs)
