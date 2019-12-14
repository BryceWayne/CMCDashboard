import numpy as np
from bokeh.io import curdoc, output_file
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Range1d, RangeTool
from bokeh.models.widgets import Slider, TextInput, Tabs, Panel, Button, DataTable, Div, CheckboxGroup
from bokeh.models.widgets import NumberFormatter, TableColumn, Dropdown, RadioButtonGroup, Select
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
	LENGTH = 30
	window1, window2 = LENGTH, 7*LENGTH
	data['Daily MA'] = data['Close**'].rolling(window=window1).mean()
	data['Weekly MA'] = data['Close**'].rolling(window=window2).mean()
	data['Risk'] = data['Daily MA']/data['Weekly MA']
	min_max_scaler = preprocessing.MinMaxScaler()
	np_scaled = min_max_scaler.fit_transform(data[['Risk']])
	data['Risk'] = np_scaled
	for _ in range(1, 10):
		data[f"L{_}"] = _/10*np.ones_like(data['Close**'])
	return data

df = get_data()
source = ColumnDataSource(df)

"""
SETUP PLOTS
"""
''' INTRO '''
intro = Select(title="Cryptocurrency", value="Bitcoin",
               options=['Bitcoin', 'Ethereum', 'Litecoin', 'Verge', 'Chainlink', 'Tezos', 'XRP', 'EOS', 'Stellar', 'Cardano', '0x'])

''' PRICE '''
price = figure(plot_height=WINDOW, plot_width=int(PHI*WINDOW), title=intro.value, tools="crosshair,pan,reset,save,wheel_zoom", x_axis_type="datetime")
price.line(x='Date', y='Close**', line_width=1, line_alpha=0.6, source=source)
price.xaxis.major_label_orientation = np.pi/4
price.yaxis.axis_label = 'Price'
price.grid.grid_line_alpha=0.3

# select = figure(title="Drag the middle and edges of the selection box to change the range above",
#                 plot_height=130, plot_width=WINDOW, y_range=price.y_range,
#                 x_axis_type="datetime", y_axis_type=None, x_range=(df['Date'].iloc[0], df['Date'].iloc[-1]),
#                 tools="", toolbar_location=None, background_fill_color="#efefef")

# price_range = RangeTool(x_range=price.x_range)
# price_range.overlay.fill_color = "navy"
# price_range.overlay.fill_alpha = 0.1618

# select.line('Date', 'Close**', source=source)
# select.ygrid.grid_line_color = None
# select.add_tools(price_range)
# select.toolbar.active_multi = price_range

''' MOVING AVERAGE'''
ma = figure(plot_height=WINDOW, plot_width=int(PHI*WINDOW), title="Moving Averages", tools="crosshair,pan,reset,save,wheel_zoom", x_axis_type="datetime")
ma.xaxis.major_label_orientation = np.pi/4
ma.grid.grid_line_alpha=0.3
ma.line(x='Date', y="Daily MA", line_width=1, line_alpha=1, source=source, line_color='red', legend_label='Daily MA')
ma.line(x='Date', y="Weekly MA", line_width=1.618, line_alpha=0.6, source=source, line_color='green', legend_label='Weekly MA')
ma_slider = Slider(start=2, end=360, value=30, step=1, title="Moving Average Period")

risk = figure(plot_height=WINDOW, plot_width=int(PHI*WINDOW), title="Risk", tools="crosshair,pan,reset,save,wheel_zoom", x_axis_type="datetime")
risk.xaxis.major_label_orientation = np.pi/4
risk.grid.grid_line_alpha=0.3
risk.line(x='Date', y="Risk", line_width=1, line_alpha=1, source=source, line_color='red', legend_label='Risk')
risk.line(x='Date', y="L1", source=source, line_width=1, alpha=0.5, line_color='green', legend_label='Optimal Buy')
risk.line(x='Date', y="L2", source=source, line_width=1, alpha=0.8, line_color='blue')
risk.line(x='Date', y="L3", source=source, line_width=1, alpha=0.6, line_color='blue')
risk.line(x='Date', y="L4", source=source, line_width=1, alpha=0.4, line_color='blue')
risk.line(x='Date', y="L5", source=source, line_width=1, alpha=0.4, line_color='blue')
risk.line(x='Date', y="L6", source=source, line_width=1, alpha=0.6, line_color='blue')
risk.line(x='Date', y="L7", source=source, line_width=1, alpha=0.8, line_color='blue')
risk.line(x='Date', y="L8", source=source, line_width=1, alpha=1, line_color='blue')
risk.line(x='Date', y="L9", source=source, line_width=1, alpha=0.5, line_color='black', legend_label='Optimal Sell')

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
	
intro.on_change('value', select_crypto)

def change_MA_period(attr, old, new):
	df = pd.DataFrame(source.data)
	# print(data.head())
	df['Daily MA'] = df['Close**'].rolling(window=ma_slider.value).mean()
	df['Weekly MA'] = df['Close**'].rolling(window=7*ma_slider.value).mean()
	source.data = df.to_dict('list')

ma_slider.on_change('value', change_MA_period)

# Set up layouts and add to document

tab0 = row(intro)
tab0 = Panel(child=tab0, title="Crypto Selection")

tab1 = row(column(price), width=int(PHI*400))
tab1 = Panel(child=tab1, title="Price")

tab2 = row(ma, column(ma_slider), width=int(PHI*400))
tab2 = Panel(child=tab2, title="Moving Averages")
tab3 = row(risk, width=int(PHI*400))

tab3 = Panel(child=tab3, title="Risk")

tabs = Tabs(tabs=[tab0, tab1, tab2, tab3])

curdoc().title = "CMC Dashboard"
curdoc().theme = 'caliber'
curdoc().add_root(tabs)
