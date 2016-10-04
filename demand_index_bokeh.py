import numpy as np
import airpy as ap
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.layouts import layout, widgetbox
from bokeh.io import curdoc
from os.path import dirname, join

# Header Page
header = Div(text = open(join(dirname(__file__), "description.html")).read(), width = 1600)

# Data Processing
data = ap.presto("SELECT DISTINCT dim_location, lat, long, searches, viewers, contacts, requests FROM robert.local_demand_index WHERE ds_night = '2016-10-10';")
source = ColumnDataSource(data = dict(dim_location = data['dim_location'], 
                                      lat = data['lat'], 
                                      lng = data['long'],
                                      searches = data['searches'],
                                      viewers = data['viewers'],
                                      contacts = data['contacts'],
                                      requests = data['requests']))

colors = ["#%02x%02x%02x" % (int(s*100), int(s*100), 150) for s in data['searches']]


# output to static HTML file (with CDN resources)
# output_file("local_demand_index.html", title = "Local Demand Index", mode = "cdn")

TOOLS = "resize, crosshair, pan, wheel_zoom, box_zoom, reset, box_select, lasso_select, hover"

# create a new plot with the tools above, and explicit ranges
p = figure(tools = TOOLS, 
           x_range = (-180, 180), 
           y_range = (-90, 180),
           plot_width = 1600,
           plot_height = 1200)

# add a circle renderer with vectorized colors and sizes
p.circle(x = 'lng', y = 'lat', radius = 'searches', fill_color = colors, fill_alpha = 0.6, line_color = None, source = source)

# Add tooltip
p.select_one(HoverTool).tooltips = [
            ("dim_location", "@dim_location"),
            ("Lat", "@lat"),
            ("Long", "@lng"),
            ("Number Of Searches", "@searches")
        ]

# show the results
# show(p)

l = layout([
    [header],
    [p],
])

show(l)
# curdoc().add_root(l)
# curdoc().title = "Supply and Demand Index"