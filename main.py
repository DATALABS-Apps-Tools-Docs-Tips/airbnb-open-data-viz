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
                          CategoricalColorMapper,
                          LabelSet)
from bokeh.models.glyphs import Circle
from bokeh.models.widgets import Slider, TextInput, Select, Button
from bokeh.palettes import Viridis
from os.path import dirname, join
from data import process_map_data, process_ts_data

zip_date_ranges, countries_list, source, sources = process_map_data(end_date = '2016-01-01')
markets_list, ts_event, ts_events, ts_source, ts_sources = process_ts_data(end_date = '2017-12-31')
START_IDX = zip_date_ranges[0][0]
END_IDX = zip_date_ranges[-1][0]

# zip_date_ranges = curdoc().zip_date_ranges
# countries_list = curdoc().countries_list
# source = curdoc().source
# sources = curdoc().sources
# markets_list = curdoc().markets_list
# ts_event = curdoc().ts_event
# ts_events = curdoc().ts_events
# ts_source = curdoc().ts_source
# ts_sources = curdoc().ts_sources
# START_IDX = curdoc().zip_date_ranges[0][0]
# END_IDX = curdoc().zip_date_ranges[-1][0]


# --------------------------------- # 
#         Map Configuration         #
# --------------------------------- # 
# https://snazzymaps.com/style/80/cool-grey

STYLE = '[{"featureType":"administrative","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"administrative.country","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"administrative.province","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"visibility":"on"},{"color":"#e3e3e3"}]},{"featureType":"landscape.natural","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"color":"#cccccc"}]},{"featureType":"road","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit.line","elementType":"geometry","stylers":[{"visibility":"off"}]},{"featureType":"transit.line","elementType":"labels.text","stylers":[{"visibility":"off"}]},{"featureType":"transit.station.airport","elementType":"geometry","stylers":[{"visibility":"off"}]},{"featureType":"transit.station.airport","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"geometry","stylers":[{"color":"#FFFFFF"}]},{"featureType":"water","elementType":"labels","stylers":[{"visibility":"off"}]}]'
API_KEY = 'AIzaSyCdiLtH-kS3uy_LfnW7d1sSak7zWxPbJn8'
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
palette = Viridis.get(256, None)
palette = [palette[i] for i in np.random.randint(1, 256, 168)]
color_mapper = CategoricalColorMapper(palette = palette, factors = countries_list)
circles = Circle(x = "long", 
                 y = "lat", 
                 radius = "searches", 
                 fill_color = {'field': 'dim_country_name', 'transform': color_mapper},
                 fill_alpha = 0.8, 
                 line_color = None)
plot.add_glyph(source, circles)

label = Label(x = -100, y = -10, text= str(zip_date_ranges[0][1]), text_font_size = '70pt', text_color = '#FFDE8D')
plot.add_layout(label)

hover = HoverTool(
            tooltips = [
                ("dim_market", "@dim_market"),
                ("dim_country", "@dim_country_name"),
            ]
        )
plot.add_tools(PanTool(), WheelZoomTool(), hover, BoxZoomTool(), ResetTool())

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

slider = Slider(start = START_IDX, end = END_IDX, value = START_IDX, step = 1, title = "Date")
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
ts_figure = figure(webgl = True, width = 1600, height = 400, x_axis_type = "datetime", title = "Demand Index")
ts_figure.circle('ds_night', 'searches_index', color = 'navy', legend = 'Demand Index', source = ts_source)
ts_figure.line('ds_night', 'searches_index', color = 'navy', legend = 'Demand Index', source = ts_source)

labels = LabelSet(x='ds_night', y='searches_index', text='event', level='glyph', source=ts_event)

ts_hover = HoverTool(
            tooltips = [
                ("Check-in Date", "@date"),
            ]
        )
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
    [button], #slider],
    [plot],
    [ts_header],
    [market_selector],
    [ts_figure]
])

curdoc().add_root(layout)
curdoc().title = "Demand Index"