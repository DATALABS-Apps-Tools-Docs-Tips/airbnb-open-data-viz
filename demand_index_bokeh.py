import numpy as np

from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
import airpy as ap


# prepare some data
# presto:default> select max(lat) as max_lat, min(lat) as min_lat, max(long) as max_long, min(long) as min_long from robert.local_demand_index;
#       max_lat      |       min_lat       |      max_long      |      min_long
# -------------------+---------------------+--------------------+---------------------
#  72.86467170715332 | -58.799312591552734 | 175.84075927734375 | -150.38241577148438

data = ap.presto("SELECT DISTINCT dim_location, lat, long, searches, viewers, contacts, requests FROM robert.local_demand_index WHERE ds_night = '2016-10-10';")
# MAX_searches = data['searches'].max()
source = ColumnDataSource(data = dict(dim_location = data['dim_location'], 
                                      lat = data['lat'], 
                                      lng = data['long'],
                                      searches = data['searches'],
                                      viewers = data['viewers'],
                                      contacts = data['contacts'],
                                      requests = data['requests']))

# N = 4000
# x = np.random.random(size=N) * 100
# y = np.random.random(size=N) * 100
# radii = np.random.random(size=N) * 1.5
# colors = [
#     "#%02x%02x%02x" % (int(r), int(g), 150) for r, g in zip(50+2*x, 30+2*y)
# ]

colors = ['#d7be96'] * data.shape[0]


# output to static HTML file (with CDN resources)
output_file("local_demand_index.html", title="Local Demand Index", mode="cdn")

TOOLS = "resize, crosshair, pan, wheel_zoom, box_zoom, reset, box_select, lasso_select"

# create a new plot with the tools above, and explicit ranges
p = figure(tools = TOOLS, x_range = (-180,180), y_range = (-90,180))

# add a circle renderer with vectorized colors and sizes
p.circle(x = 'lng', y = 'lat', radius = 'searches', fill_color = colors, fill_alpha = 0.6, line_color = None, source = source)

# show the results
show(p)