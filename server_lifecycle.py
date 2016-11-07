import numpy as np
import airpy as ap
import pandas as pd
import data
from bokeh.models import ColumnDataSource

def on_server_load(server_context):
    # zip_date_ranges, countries_list, source, sources = data.process_map_data(end_date = '2016-10-10')
    # markets_list, ts_event, ts_events, ts_source, ts_sources = data.process_ts_data(end_date = '2017-12-31')
    print "---------------------------------------"
    print server_context.__dict__
    # setattr(server_context, 'zip_date_ranges', zip_date_ranges)
    # setattr(server_context, 'countries_list', countries_list)
    pass

def on_session_created(session_context):
    print "\nLooks like the session is working ... wicked cool\n"
    zip_date_ranges, countries_list, source, sources = data.process_map_data(end_date = '2016-10-10')
    setattr(session_context._document, 'zip_date_ranges', zip_date_ranges)
    setattr(session_context._document, 'countries_list', countries_list)
    setattr(session_context._document, 'source', source)
    setattr(session_context._document, 'sources', sources)

    markets_list, ts_event, ts_events, ts_source, ts_sources = data.process_ts_data(end_date = '2017-12-31')
    setattr(session_context._document, 'markets_list', markets_list)
    setattr(session_context._document, 'ts_event', ts_event)
    setattr(session_context._document, 'ts_events', ts_events)
    setattr(session_context._document, 'ts_source', ts_source)
    setattr(session_context._document, 'ts_sources', ts_sources)
    
    print "Done with operations on session creation..."