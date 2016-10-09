import numpy as np
import airpy as ap
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool, Div, GMapPlot, GMapOptions, DataRange1d, PanTool, WheelZoomTool
from bokeh.models.glyphs import Circle
from bokeh.layouts import layout, widgetbox
from bokeh.io import curdoc
from os.path import dirname, join

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

# Header Page
header = Div(text = open(join(dirname(__file__), "description.html")).read(), width = 1600)

# Data Processing
data = ap.presto("SELECT DISTINCT dim_location, dim_market, lat, long, searches, viewers, contacts, requests FROM robert.local_demand_index WHERE ds_night = '2016-10-10';")
source = ColumnDataSource(data = dict(dim_location = data['dim_location'], 
                                      dim_market = data['dim_market'],
                                      lat = data['lat'], 
                                      lng = data['long'],
                                      searches =  data['searches'],
                                      viewers = data['viewers'],
                                      contacts = data['contacts'],
                                      requests = data['requests'],
                                      colors = ["#%02x%02x%02x" % (int(s*100), int(s*100), 150) for s in data['searches']]))

hover = HoverTool(
            tooltips=[
                ("dim_location", "@dim_location"),
                ("dim_market", "@dim_market"),
                ("Lat", "@lat"),
                ("Long", "@lng"),
                ("Number Of Searches", "@searches")
            ]
        )

circles = Circle(x = "lng", y = "lat", fill_color = "colors", fill_alpha = 0.8, line_color = None)
plot.add_glyph(source, circles)
plot.add_tools(PanTool(), WheelZoomTool(), hover)

l = layout([
    [header],
    [plot],
])

show(l)