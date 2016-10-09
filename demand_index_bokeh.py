import numpy as np
import airpy as ap
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool, Div, GMapPlot, GMapOptions, DataRange1d, PanTool, WheelZoomTool, BoxSelectTool
from bokeh.models.glyphs import Circle
from bokeh.layouts import layout, widgetbox
from bokeh.io import curdoc
from os.path import dirname, join

# Header Page
header = Div(text = open(join(dirname(__file__), "description.html")).read(), width = 1600)

# Map configuration
# https://snazzymaps.com/style/80/cool-grey
STYLE = '[{"featureType":"administrative","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"administrative.country","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"administrative.province","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"visibility":"on"},{"color":"#e3e3e3"}]},{"featureType":"landscape.natural","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"color":"#cccccc"}]},{"featureType":"road","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit.line","elementType":"geometry","stylers":[{"visibility":"off"}]},{"featureType":"transit.line","elementType":"labels.text","stylers":[{"visibility":"off"}]},{"featureType":"transit.station.airport","elementType":"geometry","stylers":[{"visibility":"off"}]},{"featureType":"transit.station.airport","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"geometry","stylers":[{"color":"#FFFFFF"}]},{"featureType":"water","elementType":"labels","stylers":[{"visibility":"off"}]}]'
API_KEY = 'AIzaSyCdiLtH-kS3uy_LfnW7d1sSak7zWxPbJn8'

map_options = GMapOptions(lat = 0, lng = 0, map_type = "roadmap", zoom = 3, styles = STYLE)

plot = GMapPlot(
    x_range = DataRange1d(), 
    y_range = DataRange1d(), 
    map_options = map_options, 
    plot_width = 1600, 
    plot_height = 1200,
    api_key = API_KEY,
)

# Data Processing
data = ap.presto("SELECT DISTINCT dim_location, dim_market, lat, long, searches, viewers, contacts, requests, ds_night FROM robert.local_demand_index WHERE ds_night >= '2016-10-10' AND ds_night <= '2016-10-17';")
data['ds_night'] = data['ds_night'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
data.sort(columns = 'ds_night', inplace = True)
source = ColumnDataSource(data = dict(dim_location = data['dim_location'], 
                                      dim_market = data['dim_market'],
                                      lat = data['lat'], 
                                      lng = data['long'],
                                      searches =  100000 * data['searches'],
                                      ts_searches = data['searches'],
                                      viewers = data['viewers'],
                                      contacts = data['contacts'],
                                      requests = data['requests'],
                                      ds_night = np.array(data['ds_night'], dtype = np.datetime64),
                                      colors = ["#%02x%02x%02x" % (int(s*100), int(s*100), 150) for s in data['searches']]))

# ts = ap.presto("SELECT DISTINCT dim_location, dim_market, lat, long, searches, viewers, contacts, requests, ds_night FROM robert.local_demand_index WHERE ds_night >= '2016-10-10' AND ds_night <= '2017-01-01' AND dim_market = 'San Francisco';")
# ts['ds_night'] = ts['ds_night'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
# ts.sort(columns = 'ds_night', inplace = True)
# ts_source = ColumnDataSource(data = dict(dim_location = ts['dim_location'], 
#                                          dim_market = ts['dim_market'],
#                                          lat = ts['lat'], 
#                                          lng = ts['long'],
#                                          searches =  ts['searches'],
#                                          viewers = ts['viewers'],
#                                          contacts = ts['contacts'],
#                                          requests = ts['requests'],
#                                          ds_night = np.array(ts['ds_night'], dtype = np.datetime64),
#                                          colors = ["#%02x%02x%02x" % (int(s*100), int(s*100), 150) for s in ts['searches']]))


# Visulaization Configuration
hover = HoverTool(
            tooltips=[
                ("dim_location", "@dim_location"),
                ("dim_market", "@dim_market"),
                ("Lat", "@lat"),
                ("Long", "@lng"),
                ("Number Of Searches", "@searches")
            ]
        )

circles = Circle(x = "lng", y = "lat", radius = "searches", fill_color = "colors", fill_alpha = 0.8, line_color = None)
plot.add_glyph(source, circles)
plot.add_tools(PanTool(), WheelZoomTool(), hover, BoxSelectTool())

ts_figure = figure(width = 1600, height = 400, x_axis_type = "datetime")
ts_figure.circle('ds_night', 'searches', color = 'navy', legend = 'Demand Index', source = source)
ts_figure.line('ds_night', 'searches', color = 'navy', legend = 'Demand Index', source = source)
ts_figure.add_tools(HoverTool(), BoxSelectTool())

l = layout([
    [header],
    [plot],
    [ts_figure]
])

show(l)