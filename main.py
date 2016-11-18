from __future__ import division
import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import layout, widgetbox
from bokeh.plotting import figure, output_file, show
from bokeh.models import (ColumnDataSource, Label,
                          GMapPlot, GMapOptions,
                          DataRange1d, Range1d,
                          HoverTool, Div,
                          PanTool, BoxZoomTool,
                          WheelZoomTool, BoxSelectTool, ResetTool,
                          ColorBar,
                          LabelSet, annotations)
from bokeh.models.mappers import LinearColorMapper
from bokeh.models.glyphs import Circle
from bokeh.models.widgets import Slider, TextInput, Select, Button
from bokeh.palettes import Viridis, Viridis10
from os.path import dirname, join
from datetime import datetime, timedelta
from data import process_map_data, process_ts_data

zip_date_ranges, countries_list, source, sources = process_map_data(end_date = '2017-01-10')
markets_list, ts_event, ts_events, ts_source, ts_sources = process_ts_data(end_date = '2017-12-31')
START_IDX = zip_date_ranges[0][0]
END_IDX = zip_date_ranges[-1][0]

def totimestamp(dt, epoch=datetime(1970,1,1)):
  td = dt - epoch
  return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6

# --------------------------------- # 
#         Map Configuration         #
# --------------------------------- # 
# https://snazzymaps.com/style/80/cool-grey

STYLE = '[{"featureType":"administrative","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"administrative.country","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"administrative.province","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"visibility":"on"},{"color":"#e3e3e3"}]},{"featureType":"landscape.natural","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"color":"#cccccc"}]},{"featureType":"road","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit.line","elementType":"geometry","stylers":[{"visibility":"off"}]},{"featureType":"transit.line","elementType":"labels.text","stylers":[{"visibility":"off"}]},{"featureType":"transit.station.airport","elementType":"geometry","stylers":[{"visibility":"off"}]},{"featureType":"transit.station.airport","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"geometry","stylers":[{"color":"#FFFFFF"}]},{"featureType":"water","elementType":"labels","stylers":[{"visibility":"off"}]}]'
API_KEY = 'AIzaSyCdiLtH-kS3uy_LfnW7d1sSak7zWxPbJn8'
map_options = GMapOptions(lat = 0, lng = 0, map_type = "roadmap", zoom = 3, styles = STYLE)

plot = GMapPlot(
    #webgl = True,
    x_range = Range1d(-180, 180), 
    y_range = Range1d(-90, 90), 
    map_options = map_options, 
    plot_width = 1600, 
    plot_height = 1200,
    api_key = API_KEY,
)

circles = Circle(x = "long", 
                 y = "lat", 
                 radius = "searches", 
                 fill_color = "colors",
                 fill_alpha = 0.8, 
                 line_color = None)
plot.add_glyph(source, circles)

label = Label(x = -100, y = -10, text= str(zip_date_ranges[0][1]), text_font_size = '70pt', text_color = '#FFDE8D')
plot.add_layout(label)

color_mapper = LinearColorMapper(palette=['#FDE724','#B2DD2C','#6BCD59','#35B778','#1E9C89','#25828E','#30678D','#3E4989','#472777','#440154'],
                                 low=int(min(source.data.get('searches'))/50000),
                                 high=int(max(source.data.get('searches'))/50000))
color_bar = ColorBar(color_mapper=color_mapper, orientation='horizontal',
                     location='bottom_left', scale_alpha=0.7)
plot.add_layout(color_bar)

hover = HoverTool(
            tooltips = [
                ("Market", "@dim_market"),
                ("Country", "@dim_country_name"),
            ]
        )
plot.add_tools(PanTool(), WheelZoomTool(), hover)

# --------------------------------- # 
#     Map Animation Interaction     #
# --------------------------------- #
def animate_update():
    date_ix = slider.value + 1
    if date_ix > END_IDX:
        date_ix = START_IDX
    slider.value = date_ix


def slider_update(attrname, old, new):
    date_ix = slider.value
    label.text = str(zip_date_ranges[date_ix][1])
    source.data = sources[date_ix].data

slider = Slider(start = START_IDX, end = END_IDX, value = START_IDX, step = 1, title = "Number Of Days Forward")
slider.on_change('value', slider_update)


def animate():
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        curdoc().add_periodic_callback(animate_update, 1000)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(animate_update)

button = Button(label= '► Play', width = 60)
button.on_click(animate)

# --------------------------------- # 
#     Time Series Configuration     #
# --------------------------------- #
ts_figure = figure(webgl = True, width = 1600, height = 400, x_axis_type = "datetime")
ts_figure.circle('ds_night', 'searches_index', size=2, color = 'navy', legend = 'Demand Index', source = ts_source)
ts_figure.line('ds_night', 'searches_index', color = 'navy', legend = 'Demand Index', source = ts_source)

labels = LabelSet(x='ds_night', y='searches_index', text='event', level='glyph', source=ts_event)

ts_hover = HoverTool(
            tooltips = [
                ("Check-in Date", "@date"),
            ]
        )
past_box = annotations.BoxAnnotation(left=totimestamp(datetime(2015,11,15))*1000,
                                     right=totimestamp(datetime(2016,11,16))*1000,
                                     fill_color='#9CA299', fill_alpha=0.1)

future_box = annotations.BoxAnnotation(left=totimestamp(datetime(2016,11,16))*1000,
                                     right=totimestamp(datetime(2017,06,15))*1000,
                                     fill_color='#FFB400', fill_alpha=0.1)

ts_figure.add_layout(past_box)
ts_figure.add_layout(future_box)
ts_figure.add_layout(labels)
ts_figure.add_tools(ts_hover)


# --------------------------------- # 
#      Time Series Interaction      #
# --------------------------------- #
market_selector = Select(title = "Market", value = "Milan", options = markets_list)

def market_selector_update(attrname, old, new):
    market = market_selector.value
    ts_source.data = ts_sources[market].data
    ts_event.data = ts_events[market].data

market_selector.on_change('value', market_selector_update)


# --------------------------------- # 
#            Final Layout           #
# --------------------------------- #
map_header = Div(text = open(join(dirname(__file__), "templates/map.html")).read(), width = 1600)
ts_header = Div(text = open(join(dirname(__file__), "templates/timeseries.html")).read(), width = 1600)

layout = layout([
    [map_header],
    [button, slider],
    [plot],
    [ts_header],
    [market_selector],
    [ts_figure]
],
sizing_mode='scale_width')

curdoc().add_root(layout)
curdoc().title = "Demand Index"