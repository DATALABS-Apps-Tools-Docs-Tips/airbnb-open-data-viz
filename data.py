import numpy as np
import airpy as ap
import pandas as pd
from bokeh.models import ColumnDataSource

def process_data():
    """The main function to query data from demand index table"""

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
        ds_night <= '2017-01-01'
    ) ldi
    JOIN core_data.dim_markets dm
    ON (ldi.dim_market = dm.dim_market)
    JOIN core_data.dim_country_groups dcg
    ON (dm.dim_country = dcg.dim_country)
    WHERE
        dm.ds = '2016-10-01'
    ;
    '''

    data = ap.presto(query)

    data['ds_year'] = data['ds_night'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d').year)
    data['ds_month'] = data['ds_night'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d').month)
    data['ds_day'] = data['ds_night'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d').day)
    data.sort_values(['dim_location', 'ds_night'], inplace = True)
    data['searches'] = 100000 * data['searches']

    sources = {}
    date_ranges = data.ds_night.unique()
    date_ranges.sort()

    for i, ds_night in enumerate(date_ranges):
        data_ds_night = data.loc[data.ds_night == ds_night, :]
        sources[i] = ColumnDataSource(data_ds_night)

    source = sources.get(0, None)
    zip_date_ranges = zip(range(len(date_ranges) + 1), date_ranges)

    print "Finished processing ... "

    return zip_date_ranges, source, sources
