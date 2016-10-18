import numpy as np
import airpy as ap
import pandas as pd
from bokeh.models import ColumnDataSource

def process_map_data(end_date):
    """The main function to query data for map viz"""

    query = '''
    SELECT
          ldi.*
        , dcg.dim_country_name
    FROM 
    (SELECT DISTINCT 
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
        ds_night >= '2016-10-01' AND 
        ds_night <= '{end_date}'
    ) ldi
    JOIN core_data.dim_markets dm
    ON (ldi.dim_market = dm.dim_market)
    JOIN core_data.dim_country_groups dcg
    ON (dm.dim_country = dcg.dim_country)
    WHERE
        dm.ds = '2016-10-01'
    ;
    '''.format(end_date = end_date)

    data = ap.presto(query)
    
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

    query = '''
    SELECT 
        * 
    FROM 
        pricing.market_demand_index
    WHERE
        ds_night >= '2016-10-01' AND 
        ds_night <= '{end_date}' AND
        ds = '2016-10-15'
    ;
    '''.format(end_date = end_date)

    ts_data = ap.presto(query)
    ts_data['ds_night'] = ts_data['ds_night'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
    ts_data.sort_values(['dim_location', 'ds_night'], inplace = True)

    ts_sources = {}
    markets_list = ts_data.dim_location.unique().tolist()
    
    for market in markets_list:
        data_for_market = ts_data.loc[ts_data.dim_location == market, :]
        ts_sources[market] = ColumnDataSource(data_for_market)

    ts_source = ts_sources.get('Los Angeles', None)

    print "Finished processing [ts data] ... "
    print "{min_date} and {max_date}".format(min_date = ts_data.ds_night.min(), max_date = ts_data.ds_night.max())

    return markets_list, ts_source, ts_sources

if __name__ == "__main__":
    print "[data.py] is being run independently"

