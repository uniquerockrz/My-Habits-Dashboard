import streamlit as st
import gspread
import pandas as pd
import arrow

secrets_file = 'credentials.json'

gc = gspread.service_account(filename=secrets_file)
g_sheet = gc.open_by_key('1chpKg4g_ReVQ4ciV2PxL_Y3S5hf5iy93OX3V6n7KdjQ')
worksheet = g_sheet.worksheet('Form responses 1')
df = pd.DataFrame(worksheet.get_all_records())

df = df.rename(columns={ 
    df.columns[2]: 'pages_nonfiction',
    df.columns[3]: 'sections_datascience',
    df.columns[4]: 'minutes_meditation',
    df.columns[5]: 'sections_programming',
    df.columns[6]: 'sections_writing',
    df.columns[7]: 'minutes_focus',
    df.columns[8]: 'pages_fiction',
    df.columns[9]: 'n_projects',
    df.columns[10]: 'n_problems',
    df.columns[11]: 'n_words',
})

def get_datetime_from_date(row):
    datetime_obj = arrow.get(row.Date, 'DD/MM/YYYY').datetime
    row['datetime'] = datetime_obj
    return row

df = df.apply(get_datetime_from_date, axis=1)

def get_display_stats(df, statscol, average=False):
    dict_to_return = dict()

    this_sunday_datetime = arrow.now().ceil('week').datetime
    this_monday_datetime = arrow.now().floor('week').datetime

    this_month_end_datetime = arrow.now().ceil('month').datetime
    this_month_begin_datetime = arrow.now().floor('month').datetime

    last_sunday_datetime = arrow.now().ceil('week').shift(weeks=-1).datetime
    last_monday_datetime = arrow.now().floor('week').shift(weeks=-1).datetime

    last_month_end_datetime = arrow.now().ceil('month').shift(months=-1).datetime
    last_month_begin_datetime = arrow.now().floor('month').shift(months=-1).datetime

    this_week_df = df[(df.datetime >= this_monday_datetime) & (df.datetime <= this_sunday_datetime)]
    last_week_df = df[(df.datetime >= last_monday_datetime) & (df.datetime <= last_sunday_datetime)]

    this_week_col = this_week_df[statscol]
    last_week_col = last_week_df[statscol]

    this_month_df = df[(df.datetime >= this_month_begin_datetime) & (df.datetime <= this_month_end_datetime)]
    last_month_df = df[(df.datetime >= last_month_begin_datetime) & (df.datetime <= last_month_end_datetime)]

    this_month_col = this_month_df[statscol]
    last_month_col = last_month_df[statscol]

    this_week_dict = dict()
    this_week_dict['total'] = this_week_col.sum()
    
    last_week_dict = dict()
    last_week_dict['total'] = last_week_col.sum()

    this_month_dict = dict()
    this_month_dict['total'] = this_month_col.sum()

    last_month_dict = dict()
    last_month_dict['total'] = last_month_col.sum()

    total_dict = dict()
    total_dict['total'] = df[statscol].sum()

    if average == True:
        this_week_dict['average'] = this_week_col.mean()
        last_week_dict['average'] = last_week_col.mean()
        this_month_dict['average'] = this_month_col.mean()
        last_month_dict['average'] = last_month_col.mean()
        total_dict['average'] = df[statscol].mean()

    dict_to_return['this_week'] = this_week_dict
    dict_to_return['last_week'] = last_week_dict
    dict_to_return['this_month'] = this_month_dict
    dict_to_return['last_month'] = last_month_dict
    dict_to_return['totals'] = total_dict    

    return dict_to_return

