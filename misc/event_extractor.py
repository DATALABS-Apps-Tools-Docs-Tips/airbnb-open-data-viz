from collections import defaultdict
import pandas as pd
import datetime
import openpyxl
import re


wb = openpyxl.load_workbook('events.xlsx')

sheets = [name for name in wb.get_sheet_names()]

sheet_pattern = re.compile(r'^(.*)_(events)$')

events_final = []

for sheet_name in sheets:
    print "processing {} ...".format(sheet_name)
    sheet = wb.get_sheet_by_name(sheet_name)

    if sheet.max_row > 1:
        city = re.match(sheet_pattern, sheet_name).group(1)
        columns = list(sheet.columns)

        city_event_dict = {}

        for date, event in zip(columns[1], columns[2]):
            if date.value != 'dates':
                event_pattern = re.compile(r'^(.*)_([0-9]+)')
                event = re.match(event_pattern, event.value).group(1).replace('_', ' ').title().strip()
                city_event_dict[pd.to_datetime(date.value)] = event

        df = pd.DataFrame({"date": city_event_dict.keys(), "event": city_event_dict.values()})
        df['city'] = city
        df['year'] = df.date.dt.year
        other = pd.DataFrame(df.groupby(['event']).year.nunique())
        other.columns = ['year_cnt']
        df = df.join(other, on = 'event')
        df = df.loc[df.year_cnt > 1, :]
        df.sort(columns = ['event', 'date'])
        df['rnk'] = df.groupby(['event', 'year'])['date'].rank('dense', ascending = True)
        df = df.loc[df.rnk == 1, :]
        df.sort(columns = ['event', 'date'], inplace = True)
        events_final.append(df)

events_final = pd.concat(events_final, axis = 0)
events_final.drop(['year', 'year_cnt', 'rnk'], axis = 1, inplace = True)
events_final.to_csv('events.csv')