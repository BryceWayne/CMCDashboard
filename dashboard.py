import numpy as np
from bokeh.io import curdoc, output_file
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Range1d
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

"""
DEFAULTS
"""
plt.style.use('default')
PHI = 1.618
w = 12*60*60*1000 # half day in ms
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
	data[f'{window1} Day MA'] = data['Close**'].rolling(window=window1).mean()
	data[f'{window1} Week MA'] = data['Close**'].rolling(window=window2).mean()
	data = data[['Open*', 'High', 'Low', 'Close**', 'Volume', 'Market Cap', 'Date']]
	return data

df = get_data()
source = ColumnDataSource(df)

"""
SETUP PLOTS
"""
inc = df['Close**'] > df['Open*']
dec = df['Open*'] > df['Close**']
price = figure(plot_height=600, plot_width=int(PHI*600), title="Bitcoin", tools="crosshair,pan,reset,save,wheel_zoom", x_axis_type="datetime")
price.line(x='Date', y='Close**', line_width=1, line_alpha=0.6, source=source)
price.xaxis.major_label_orientation = np.pi/4
price.grid.grid_line_alpha=0.3
price.segment(df['Date'], df['High'], df['Date'], df['Low'], color="black")
price.vbar(df['Date'][inc], w, df['Open*'][inc], df['Close**'][inc], fill_color="#D5E1DD", line_color="black")
price.vbar(df['Date'][dec], w, df['Open*'][dec], df['Close**'][dec], fill_color="#F2583E", line_color="black")

MA = figure(plot_height=600, plot_width=int(PHI*600), title="Bitcoin", tools="crosshair,pan,reset,save,wheel_zoom", x_axis_type="datetime")
MA.line(x='Date', y='30 Day MA', line_width=1, line_alpha=0.6, source=source)
MA.line(x='Date', y='30 Week MA', line_width=1, line_alpha=0.6, source=source)
"""
SETUP WIDGETS
"""
price_div = Div(text="""<p style="border:3px; border-style:solid; border-color:#FF0000; padding: 1em;">
                    Stuff.</p>""",
                    width=300, height=130)
price_title = TextInput(title="Plot Title", value='Bitcoin')

"""
Set up callbacks
"""
def update_title(attrname, old, new):
    price.title.text = price_title.value


for t in [price_title]:
    t.on_change('value', update_title)


# Set up layouts and add to document
inputs1 = column(price_div, price_title)


tab1 = row(price, width=int(PHI*400))
tab1 = Panel(child=tab1, title="Price")
tab2 = row(MA, width=int(PHI*400))
tab2 = Panel(child=tab2, title="Moving Averages")
tabs = Tabs(tabs=[tab1, tab2])

curdoc().title = "CMC Dashboard"
curdoc().theme = 'caliber'
curdoc().add_root(tabs)
