from bokeh.io import curdoc
from bokeh.layouts import layout, widgetbox
from bokeh.plotting import figure, output_file, show
from bokeh.models import (ColumnDataSource, Label,
                          GMapPlot, GMapOptions,
                          DataRange1d, Range1d,
                          HoverTool, Div,
                          PanTool, BoxZoomTool,
                          WheelZoomTool, BoxSelectTool,
                          CategoricalColorMapper,)
from bokeh.models.glyphs import Circle
from bokeh.models.widgets import Slider, TextInput, Select, Button
from bokeh.palettes import Viridis
from os.path import dirname, join
from data import process_data

zip_date_ranges, countries_list, source, sources = process_data(end_date = '2016-10-10')
START_IDX = zip_date_ranges[0][0]
END_IDX = zip_date_ranges[-1][0]

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

color_mapper = CategoricalColorMapper(palette = Viridis.get(256, None), factors = countries_list)
circles = Circle(x = "long", 
                 y = "lat", 
                 radius = "searches", 
                 fill_color = {'field': 'dim_country_name', 'transform': color_mapper},
                 fill_alpha = 0.8, 
                 line_color = None)
plot.add_glyph(source, circles)

label = Label(x = -60, y = 0, text= str(zip_date_ranges[0][1]), text_font_size = '70pt', text_color = '#eeeeee')
plot.add_layout(label)

hover = HoverTool(
            tooltips = [
                ("dim_location", "@dim_location"),
                ("dim_market", "@dim_market"),
                ("dim_country", "@dim_country_name"),
            ]
        )
plot.add_tools(PanTool(), WheelZoomTool(), hover, BoxZoomTool())

# --------------------------------- # 
#            Interaction            #
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


# Layout
header = Div(text = open(join(dirname(__file__), "description.html")).read(), width = 1600)

layout = layout([
    [header],
    [plot],
    [button]
])

curdoc().add_root(layout)
curdoc().title = "Demand Index"