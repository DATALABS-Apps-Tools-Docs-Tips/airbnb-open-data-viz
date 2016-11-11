import numpy as np
import airpy as ap
import pandas as pd
from bokeh.models import ColumnDataSource

def process_map_data(end_date):
    """The main function to query data for map viz"""

    # query = '''
    # SELECT
    #       ldi.*
    #     , dcg.dim_country_name
    # FROM 
    # (SELECT DISTINCT 
    #       dim_location
    #     , dim_market
    #     , lat
    #     , long
    #     , searches
    #     , viewers
    #     , contacts
    #     , requests
    #     , ds_night 
    # FROM 
    #     robert.local_demand_index 
    # WHERE
    #     ds_night >= '2016-10-01' AND 
    #     ds_night <= '{end_date}'
    # ) ldi
    # JOIN core_data.dim_markets dm
    # ON (ldi.dim_market = dm.dim_market)
    # JOIN core_data.dim_country_groups dcg
    # ON (dm.dim_country = dcg.dim_country)
    # WHERE
    #     dm.ds = '2016-11-07'
    # ;
    # '''.format(end_date = end_date)

    # data = ap.presto(query)
    # data.to_csv('process_map_data.csv', encoding='utf8', index_label=False)
    data = pd.read_csv('./airbnb-open-data-viz/data/process_map_data.csv')
    
    data['searches'] = 100000 * data['searches']

    sources = {}
    date_ranges = data.ds_night.unique()
    date_ranges.sort()

    for i, ds_night in enumerate(date_ranges):
        data_ds_night = data.loc[data.ds_night == ds_night, :]
        sources[i] = ColumnDataSource(data_ds_night)

    source = sources.get(0, None)
    zip_date_ranges = zip(range(len(date_ranges) + 1), date_ranges)
    countries_list = data.dim_country_name.unique().tolist()

    print "Finished processing [map data] ... "

    return zip_date_ranges, countries_list, source, sources

def process_ts_data(end_date):
    """The main function to query data for time series viz"""

    # query_top_cities = '''
    # SELECT
    #     dim_location
    # FROM (
    #     SELECT
    #           dim_market AS dim_location
    #         , COUNT(DISTINCT id_user) AS ct
    #     FROM 
    #         bnamih.hco_dim_hosts
    #     WHERE
    #         ds = '2016-11-07' AND
    #         dim_market != '-unknown-' AND 
    #         dim_market NOT LIKE '%Other%'
    #     GROUP BY
    #         dim_market
    #     ORDER BY
    #         ct DESC
    # ) LIMIT 100
    # '''
    # selective_dim_location = ap.presto(query_top_cities)
    # selective_dim_location.to_csv('selective_dim_location.csv', encoding='utf8', index_label=False)
    selective_dim_location = pd.read_csv('./airbnb-open-data-viz/data/selective_dim_location.csv')
    selective_dim_location = selective_dim_location.dim_location.tolist()

    # query = '''
    # SELECT 
    #     * 
    # FROM 
    #     pricing.market_demand_index
    # WHERE
    #     ds_night >= '2016-10-01' AND 
    #     ds_night <= '{end_date}' AND
    #     ds = '2016-11-07'
    # ;
    # '''.format(end_date = end_date)
    # ts_data = ap.presto(query)
    # ts_data['ds_night'] = pd.to_datetime(ts_data.ds_night, format='%Y-%m-%d')
    # ts_data.sort_values(['dim_location', 'ds_night'], inplace = True)
    # ts_data = ts_data.loc[ts_data.dim_location.isin(selective_dim_location), :]
    # ts_data.to_csv('process_ts_data.csv', encoding='utf8', index_label=False)
    
    # Only display time series of the top cities
    ts_data = pd.read_csv('./airbnb-open-data-viz/data/process_ts_data.csv')
    ts_data['ds_night'] = pd.to_datetime(ts_data.ds_night)

    _events = _load_events()
    events = pd.merge(ts_data, _events, on = ['dim_location', 'ds_night'])

    ts_sources = {}
    ts_events = {}
    markets_list = ts_data.dim_location.unique().tolist()

    for market in markets_list:
        data_for_market = ts_data.loc[ts_data.dim_location == market, :]
        ts_sources[market] = ColumnDataSource(data_for_market)
        events_for_market = events.loc[events.dim_location == market, :]
        ts_events[market] = ColumnDataSource(events_for_market)

    ts_source = ts_sources.get('Milan', None)
    ts_event = ts_events.get('Milan', None)
    
    print "Finished processing [ts data] ... "

    return markets_list, ts_event, ts_events, ts_source, ts_sources

def _load_events():
    events = pd.read_csv('./airbnb-open-data-viz/data/events.csv')
    events['date'] = pd.to_datetime(events.date)
    events['date'] = events.date + pd.Timedelta(365, unit = 'd') # cheat for now
    events.columns = ['idx', 'ds_night', 'event', 'dim_location']
    events['year'] = events.ds_night.dt.year
    events = events.loc[events.year == 2016, :]
    events.drop(['idx', 'year'], axis = 1, inplace = True)
    
    return events

if __name__ == "__main__":
    print "[data.py] is being run independently"

