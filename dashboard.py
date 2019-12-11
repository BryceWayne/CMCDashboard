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
	data.set_index(data['Date'], inplace=True)
	data = data[['Open*', 'High', 'Low', 'Close**', 'Volume', 'Market Cap']]


"""
SETUP PLOTS
"""
plot1 = figure(plot_height=600, plot_width=int(PHI*600), title="Oh my Gauss")
plot1.line([1, 3, 5, 7, 9], [0, 2, 4, 6, 8], line_width=2)

"""
SETUP WIDGETS
"""
div1 = Div(text="""<p style="border:3px; border-style:solid; border-color:#FF0000; padding: 1em;">
                    Stuff.</p>""",
                    width=300, height=130)
title1 = TextInput(title="Plot Title", value='Oh my Gauss')


# Set up layouts and add to document
inputs1 = column(div1, title1)

tab1 = row(inputs1, plot1, width=int(PHI*400))
tab1 = Panel(child=tab1, title="Like a Gauss")
tabs = Tabs(tabs=[tab1])

curdoc().title = "CMC Dashboard"
curdoc().theme = 'caliber'
curdoc().add_root(tabs)
