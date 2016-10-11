import numpy as np
import airpy as ap
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import layout, widgetbox
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool, Div, GMapPlot, GMapOptions, DataRange1d, PanTool, WheelZoomTool, BoxSelectTool, Range1d
from bokeh.models.glyphs import Circle
from bokeh.models.widgets import Slider, TextInput, Select
from os.path import dirname, join

# Header Page
header = Div(text = open(join(dirname(__file__), "description.html")).read(), width = 1600)

# Map configuration
# https://snazzymaps.com/style/80/cool-grey
STYLE = '[{"featureType":"administrative","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"administrative.country","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"administrative.province","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"visibility":"on"},{"color":"#e3e3e3"}]},{"featureType":"landscape.natural","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"color":"#cccccc"}]},{"featureType":"road","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit.line","elementType":"geometry","stylers":[{"visibility":"off"}]},{"featureType":"transit.line","elementType":"labels.text","stylers":[{"visibility":"off"}]},{"featureType":"transit.station.airport","elementType":"geometry","stylers":[{"visibility":"off"}]},{"featureType":"transit.station.airport","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"geometry","stylers":[{"color":"#FFFFFF"}]},{"featureType":"water","elementType":"labels","stylers":[{"visibility":"off"}]}]'
API_KEY = 'AIzaSyCdiLtH-kS3uy_LfnW7d1sSak7zWxPbJn8'

# Data Processing
def update_source(df):
    return dict(dim_location = df['dim_location'], 
                dim_market = df['dim_market'],
                lat = df['lat'], 
                lng = df['long'],
                searches =  100000 * df['searches'],
                ts_searches = df['searches'],
                viewers = df['viewers'],
                contacts = df['contacts'],
                requests = df['requests'],
                ds_night = np.array(df['ds_night'], dtype = np.datetime64),
                colors = ["#%02x%02x%02x" % (int(s*100), int(s*100), 150) for s in df['searches']])

query = '''
SELECT DISTINCT 
      dim_location
    , dim_market
    , lat
    , long
    , searches
    , viewers
    , contacts
    , requests
    , ds_night 
FROM 
    robert.local_demand_index 
WHERE
    ds_night >= '2016-10-01' AND ds_night <= '2016-10-10'
'''
data = ap.presto(query)

data['ds_night'] = data['ds_night'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
data['ds_year'] = data['ds_night'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d').year)
data['ds_month'] = data['ds_night'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d').month)
data['ds_day'] = data['ds_night'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d').day)
data.sort_values(['dim_location', 'ds_night'], inplace = True)
source = ColumnDataSource(data = update_source(data))

# Plots Configuration
hover = HoverTool(
            tooltips = [
                ("dim_location", "@dim_location"),
                ("dim_market", "@dim_market"),
                ("Lat", "@lat"),
                ("Long", "@lng"),
                ("Number Of Searches", "@searches"),
            ]
        )
map_options = GMapOptions(lat = 0, lng = 0, map_type = "roadmap", zoom = 3, styles = STYLE)

plot = GMapPlot(
    webgl = True,
    x_range = Range1d(-180, 180), 
    y_range = Range1d(-90, 90), 
    map_options = map_options, 
    plot_width = 1600, 
    plot_height = 1200,
    api_key = API_KEY,
)

circles = Circle(x = "lng", y = "lat", radius = "searches", fill_color = "colors", fill_alpha = 0.8, line_color = None)
plot.add_glyph(source, circles)
plot.add_tools(PanTool(), WheelZoomTool(), hover, BoxSelectTool())

ts_figure = figure(webgl = True, width = 1600, height = 400, x_axis_type = "datetime", title = "Demand Index")
cr = ts_figure.circle('ds_night', 'searches', color = 'navy', legend = 'Demand Index', source = source)
#ts_figure.line('ds_night', 'searches', color = 'navy', legend = 'Demand Index', source = source)
ts_figure.add_tools(HoverTool(), BoxSelectTool())

# Visulaization Configuration
day_slider = Slider(start = 1, end = 30, value = 1, step = 1, title = "Day")

def day_slider_update(attrname, old, new):
    day = day_slider.value
    new_data = data.loc[data.ds_day >= day, :]
    source.data = update_source(new_data)

day_slider.on_change('value', day_slider_update)

cities_list = data.dim_market.unique().tolist()
market_selector = Select(title = "Market", value = "Paris", options = cities_list)

def market_selector_update(attrname, old, new):
    market = market_selector.value
    new_data = data.loc[data.dim_market == market, :]
    source.data = update_source(new_data)

market_selector.on_change('value', market_selector_update)

# Layout
layout = layout([
    [header],
    [plot],
    [market_selector],
    [day_slider],
    [ts_figure]
])

# show(layout)
curdoc().add_root(layout)
curdoc().title = "Demand Index"