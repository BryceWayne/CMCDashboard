import numpy as np
from bokeh.io import curdoc, output_file
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models.widgets import Slider, TextInput, Tabs, Panel, Button, DataTable, Div, CheckboxGroup
from bokeh.models.widgets import NumberFormatter, TableColumn, Dropdown, RadioButtonGroup, Select
from bokeh.plotting import figure
from pprint import pprint
import pandas as pd
import requests
import matplotlib.pyplot as plt
plt.style.use('default')
import datetime
from sklearn import preprocessing

"""
SETUP DATA
"""
phi = 1.618



"""
SETUP PLOTS
"""
plot1 = figure(plot_height=600, plot_width=int(phi*600), title="Oh my Gauss",
              tools="save")

"""
SETUP WIDGETS
"""
div1 = Div(text="""<p style="border:3px; border-style:solid; border-color:#FF0000; padding: 1em;">
                    Stuff.</p>""",
                    width=300, height=130)
title1 = TextInput(title="Plot Title", value='Oh my Gauss')

"""
Set up callbacks
"""
def update_title(attrname, old, new):
    plot1.title.text = title1.value


for t in [title1]:
    t.on_change('value', update_title)


# Set up layouts and add to document
inputs1 = column(div1, title1)

tab1 = row(inputs1, plot1, width=int(phi*400))
tab1 = Panel(child=tab1, title="Like a Gauss")
tabs = Tabs(tabs=[tab1])

curdoc().title = "CMC Dashboard"
curdoc().theme = 'caliber'
curdoc().add_root(tabs)
