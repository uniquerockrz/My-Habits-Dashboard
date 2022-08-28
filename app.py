import streamlit as st
import gspread
import pandas as pd
import arrow
import numpy as np

st.set_page_config(page_title='Life Statistics', page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

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

def get_total_pages(row):
    total_pages = row['pages_fiction'] + row['pages_nonfiction']
    row['n_pages'] = total_pages
    return row

df = df.apply(get_total_pages, axis=1)

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
        this_week_dict['average'] = np.nan_to_num(this_week_col.mean())
        last_week_dict['average'] = np.nan_to_num(last_week_col.mean())
        this_month_dict['average'] = np.nan_to_num(this_month_col.mean())
        last_month_dict['average'] = np.nan_to_num(last_month_col.mean())
        total_dict['average'] = np.nan_to_num(df[statscol].mean())

    dict_to_return['this_week'] = this_week_dict
    dict_to_return['last_week'] = last_week_dict
    dict_to_return['this_month'] = this_month_dict
    dict_to_return['last_month'] = last_month_dict
    dict_to_return['totals'] = total_dict    

    return dict_to_return

def get_chart_data(df):
    day_above = arrow.now().ceil('day').shift(days=-30).datetime
    
    last_30_days_df = df[(df.datetime >= day_above)]

    return last_30_days_df

last_30_days_df = get_chart_data(df)
    
st.write('# Life Statistics')

st.write('## Focus')

st.line_chart(data=last_30_days_df, x='Date', y=['minutes_focus'], width=0, height=0, use_container_width=True)

st.write('#### Totals')
minutes_focus_metrics = get_display_stats(df, 'minutes_focus', True)

col_minutes_focus_total1, col_minutes_focus_total2, col_minutes_focus_total3, col_minutes_focus_total4, col_minutes_focus_total5 = st.columns(5)
col_minutes_focus_total1.metric('This Week','{} hrs'.format(round((minutes_focus_metrics['this_week']['total'] / 60), 2)) , delta='{} hrs'.format(round(round((minutes_focus_metrics['this_week']['total'] / 60), 2) - round((minutes_focus_metrics['last_week']['total'] / 60), 2) )), delta_color="normal", help=None)
col_minutes_focus_total2.metric('Last Week','{} hrs'.format(round((minutes_focus_metrics['last_week']['total'] / 60), 2)) , delta=None, delta_color="normal", help=None)
col_minutes_focus_total3.metric('This Month','{} hrs'.format(round((minutes_focus_metrics['this_month']['total'] / 60), 2)) , delta='{} hrs'.format(round(round((minutes_focus_metrics['this_month']['total'] / 60), 2) - round((minutes_focus_metrics['last_month']['total'] / 60), 2) )), delta_color="normal", help=None)
col_minutes_focus_total4.metric('Last Month','{} hrs'.format(round((minutes_focus_metrics['last_month']['total'] / 60), 2)) , delta=None, delta_color="normal", help=None)
col_minutes_focus_total5.metric('Total','{} hrs'.format(round((minutes_focus_metrics['totals']['total'] / 60), 2)) , delta=None, delta_color="normal", help=None)

st.write('#### Averages per day')
col_minutes_focus_avg1, col_minutes_focus_avg2, col_minutes_focus_avg3, col_minutes_focus_avg4, col_minutes_focus_avg5 = st.columns(5)
col_minutes_focus_avg1.metric('This Week','{} hrs'.format(round((minutes_focus_metrics['this_week']['average'] / 60), 2)) , delta='{} hrs'.format(round(round((minutes_focus_metrics['this_week']['average'] / 60), 2) - round((minutes_focus_metrics['last_week']['average'] / 60), 2) )), delta_color="normal", help=None)
col_minutes_focus_avg2.metric('Last Week','{} hrs'.format(round((minutes_focus_metrics['last_week']['average'] / 60), 2)) , delta=None, delta_color="normal", help=None)
col_minutes_focus_avg3.metric('This Month','{} hrs'.format(round((minutes_focus_metrics['this_month']['average'] / 60), 2)) , delta='{} hrs'.format(round(round((minutes_focus_metrics['this_month']['average'] / 60), 2) - round((minutes_focus_metrics['last_month']['average'] / 60), 2) )), delta_color="normal", help=None)
col_minutes_focus_avg4.metric('Last Month','{} hrs'.format(round((minutes_focus_metrics['last_month']['average'] / 60), 2)) , delta=None, delta_color="normal", help=None)
col_minutes_focus_avg5.metric('Total','{} hrs'.format(round((minutes_focus_metrics['totals']['average'] / 60), 2)) , delta=None, delta_color="normal", help=None)

st.write('## Meditation')

st.line_chart(data=last_30_days_df, x='Date', y=['minutes_meditation'], width=0, height=0, use_container_width=True)

st.write('#### Totals')
minutes_meditation_metrics = get_display_stats(df, 'minutes_meditation', True)

col_minutes_meditation_total1, col_minutes_meditation_total2, col_minutes_meditation_total3, col_minutes_meditation_total4, col_minutes_meditation_total5 = st.columns(5)
col_minutes_meditation_total1.metric('This Week','{} mins'.format(round((minutes_meditation_metrics['this_week']['total']), 2)) , delta='{} mins'.format(round(round((minutes_meditation_metrics['this_week']['total']), 2) - round((minutes_meditation_metrics['last_week']['total']), 2) )), delta_color="normal", help=None)
col_minutes_meditation_total2.metric('Last Week','{} mins'.format(round((minutes_meditation_metrics['last_week']['total']), 2)) , delta=None, delta_color="normal", help=None)
col_minutes_meditation_total3.metric('This Month','{} mins'.format(round((minutes_meditation_metrics['this_month']['total']), 2)) , delta='{} mins'.format(round(round((minutes_meditation_metrics['this_month']['total']), 2) - round((minutes_meditation_metrics['last_month']['total']), 2) )), delta_color="normal", help=None)
col_minutes_meditation_total4.metric('Last Month','{} mins'.format(round((minutes_meditation_metrics['last_month']['total']), 2)) , delta=None, delta_color="normal", help=None)
col_minutes_meditation_total5.metric('Total','{} mins'.format(round((minutes_meditation_metrics['totals']['total']), 2)) , delta=None, delta_color="normal", help=None)

st.write('#### Averages per day')
col_minutes_meditation_avg1, col_minutes_meditation_avg2, col_minutes_meditation_avg3, col_minutes_meditation_avg4, col_minutes_meditation_avg5 = st.columns(5)
col_minutes_meditation_avg1.metric('This Week','{} mins'.format(round((minutes_meditation_metrics['this_week']['average']), 2)) , delta='{} mins'.format(round(round((minutes_meditation_metrics['this_week']['average']), 2) - round((minutes_meditation_metrics['last_week']['average']), 2) )), delta_color="normal", help=None)
col_minutes_meditation_avg2.metric('Last Week','{} mins'.format(round((minutes_meditation_metrics['last_week']['average']), 2)) , delta=None, delta_color="normal", help=None)
col_minutes_meditation_avg3.metric('This Month','{} mins'.format(round((minutes_meditation_metrics['this_month']['average']), 2)) , delta='{} mins'.format(round(round((minutes_meditation_metrics['this_month']['average']), 2) - round((minutes_meditation_metrics['last_month']['average']), 2) )), delta_color="normal", help=None)
col_minutes_meditation_avg4.metric('Last Month','{} mins'.format(round((minutes_meditation_metrics['last_month']['average']), 2)) , delta=None, delta_color="normal", help=None)
col_minutes_meditation_avg5.metric('Total','{} mins'.format(round((minutes_meditation_metrics['totals']['average']), 2)) , delta=None, delta_color="normal", help=None)

st.write('## Pages Read')

st.bar_chart(data=last_30_days_df, x='Date', y=['pages_nonfiction', 'pages_fiction'], width=0, height=0, use_container_width=True)

st.write('#### Totals')
n_pages_metrics = get_display_stats(df, 'n_pages', True)

n_pages_total1, n_pages_total2, n_pages_total3, n_pages_total4, n_pages_total5 = st.columns(5)
n_pages_total1.metric('This Week','{}'.format(round((n_pages_metrics['this_week']['total']), 2)) , delta='{}'.format(round(round((n_pages_metrics['this_week']['total']), 2) - round((n_pages_metrics['last_week']['total']), 2) )), delta_color="normal", help=None)
n_pages_total2.metric('Last Week','{}'.format(round((n_pages_metrics['last_week']['total']), 2)) , delta=None, delta_color="normal", help=None)
n_pages_total3.metric('This Month','{}'.format(round((n_pages_metrics['this_month']['total']), 2)) , delta='{}'.format(round(round((n_pages_metrics['this_month']['total']), 2) - round((n_pages_metrics['last_month']['total']), 2) )), delta_color="normal", help=None)
n_pages_total4.metric('Last Month','{}'.format(round((n_pages_metrics['last_month']['total']), 2)) , delta=None, delta_color="normal", help=None)
n_pages_total5.metric('Total','{}'.format(round((n_pages_metrics['totals']['total']), 2)) , delta=None, delta_color="normal", help=None)

st.write('#### Averages per day')
n_pages_avg1, n_pages_avg2, n_pages_avg3, n_pages_avg4, n_pages_avg5 = st.columns(5)
n_pages_avg1.metric('This Week','{}'.format(round((n_pages_metrics['this_week']['average']), 2)) , delta='{}'.format(round(round((n_pages_metrics['this_week']['average']), 2) - round((n_pages_metrics['last_week']['average']), 2) )), delta_color="normal", help=None)
n_pages_avg2.metric('Last Week','{}'.format(round((n_pages_metrics['last_week']['average']), 2)) , delta=None, delta_color="normal", help=None)
n_pages_avg3.metric('This Month','{}'.format(round((n_pages_metrics['this_month']['average']), 2)) , delta='{}'.format(round(round((n_pages_metrics['this_month']['average']), 2) - round((n_pages_metrics['last_month']['average']), 2) )), delta_color="normal", help=None)
n_pages_avg4.metric('Last Month','{}'.format(round((n_pages_metrics['last_month']['average']), 2)) , delta=None, delta_color="normal", help=None)
n_pages_avg5.metric('Total','{}'.format(round((n_pages_metrics['totals']['average']), 2)) , delta=None, delta_color="normal", help=None)

st.write('#### Non-Fiction')
n_pages_nonfiction_metrics = get_display_stats(df, 'pages_nonfiction', False)

n_pages_nonfiction_total1, n_pages_nonfiction_total2, n_pages_nonfiction_total3, n_pages_nonfiction_total4, n_pages_nonfiction_total5 = st.columns(5)
n_pages_nonfiction_total1.metric('This Week','{}'.format(round((n_pages_nonfiction_metrics['this_week']['total']), 2)) , delta='{}'.format(round(round((n_pages_nonfiction_metrics['this_week']['total']), 2) - round((n_pages_nonfiction_metrics['last_week']['total']), 2) )), delta_color="normal", help=None)
n_pages_nonfiction_total2.metric('Last Week','{}'.format(round((n_pages_nonfiction_metrics['last_week']['total']), 2)) , delta=None, delta_color="normal", help=None)
n_pages_nonfiction_total3.metric('This Month','{}'.format(round((n_pages_nonfiction_metrics['this_month']['total']), 2)) , delta='{}'.format(round(round((n_pages_nonfiction_metrics['this_month']['total']), 2) - round((n_pages_nonfiction_metrics['last_month']['total']), 2) )), delta_color="normal", help=None)
n_pages_nonfiction_total4.metric('Last Month','{}'.format(round((n_pages_nonfiction_metrics['last_month']['total']), 2)) , delta=None, delta_color="normal", help=None)
n_pages_nonfiction_total5.metric('Total','{}'.format(round((n_pages_nonfiction_metrics['totals']['total']), 2)) , delta=None, delta_color="normal", help=None)

st.write('#### Fiction')
n_pages_fiction_metrics = get_display_stats(df, 'pages_fiction', False)

n_pages_fiction_total1, n_pages_fiction_total2, n_pages_fiction_total3, n_pages_fiction_total4, n_pages_fiction_total5 = st.columns(5)
n_pages_fiction_total1.metric('This Week','{}'.format(round((n_pages_fiction_metrics['this_week']['total']), 2)) , delta='{}'.format(round(round((n_pages_fiction_metrics['this_week']['total']), 2) - round((n_pages_fiction_metrics['last_week']['total']), 2) )), delta_color="normal", help=None)
n_pages_fiction_total2.metric('Last Week','{}'.format(round((n_pages_fiction_metrics['last_week']['total']), 2)) , delta=None, delta_color="normal", help=None)
n_pages_fiction_total3.metric('This Month','{}'.format(round((n_pages_fiction_metrics['this_month']['total']), 2)) , delta='{}'.format(round(round((n_pages_fiction_metrics['this_month']['total']), 2) - round((n_pages_fiction_metrics['last_month']['total']), 2) )), delta_color="normal", help=None)
n_pages_fiction_total4.metric('Last Month','{}'.format(round((n_pages_fiction_metrics['last_month']['total']), 2)) , delta=None, delta_color="normal", help=None)
n_pages_fiction_total5.metric('Total','{}'.format(round((n_pages_fiction_metrics['totals']['total']), 2)) , delta=None, delta_color="normal", help=None)

st.write('## Data Science')

st.area_chart(data=last_30_days_df, x='Date', y=['sections_datascience', 'n_projects'], width=0, height=0, use_container_width=True)

st.write('#### Sections')
sections_datascience_metrics = get_display_stats(df, 'sections_datascience', False)

sections_datascience_total1, sections_datascience_total2, sections_datascience_total3, sections_datascience_total4, sections_datascience_total5 = st.columns(5)
sections_datascience_total1.metric('This Week','{}'.format(round((sections_datascience_metrics['this_week']['total']), 2)) , delta='{}'.format(round(round((sections_datascience_metrics['this_week']['total']), 2) - round((sections_datascience_metrics['last_week']['total']), 2) )), delta_color="normal", help=None)
sections_datascience_total2.metric('Last Week','{}'.format(round((sections_datascience_metrics['last_week']['total']), 2)) , delta=None, delta_color="normal", help=None)
sections_datascience_total3.metric('This Month','{}'.format(round((sections_datascience_metrics['this_month']['total']), 2)) , delta='{}'.format(round(round((sections_datascience_metrics['this_month']['total']), 2) - round((sections_datascience_metrics['last_month']['total']), 2) )), delta_color="normal", help=None)
sections_datascience_total4.metric('Last Month','{}'.format(round((sections_datascience_metrics['last_month']['total']), 2)) , delta=None, delta_color="normal", help=None)
sections_datascience_total5.metric('Total','{}'.format(round((sections_datascience_metrics['totals']['total']), 2)) , delta=None, delta_color="normal", help=None)

st.write('#### Projects')
n_projects_metrics = get_display_stats(df, 'n_projects', False)

n_projects_total1, n_projects_total2, n_projects_total3, n_projects_total4, n_projects_total5 = st.columns(5)
n_projects_total1.metric('This Week','{}'.format(round((n_projects_metrics['this_week']['total']), 2)) , delta='{}'.format(round(round((n_projects_metrics['this_week']['total']), 2) - round((n_projects_metrics['last_week']['total']), 2) )), delta_color="normal", help=None)
n_projects_total2.metric('Last Week','{}'.format(round((n_projects_metrics['last_week']['total']), 2)) , delta=None, delta_color="normal", help=None)
n_projects_total3.metric('This Month','{}'.format(round((n_projects_metrics['this_month']['total']), 2)) , delta='{}'.format(round(round((n_projects_metrics['this_month']['total']), 2) - round((n_projects_metrics['last_month']['total']), 2) )), delta_color="normal", help=None)
n_projects_total4.metric('Last Month','{}'.format(round((n_projects_metrics['last_month']['total']), 2)) , delta=None, delta_color="normal", help=None)
n_projects_total5.metric('Total','{}'.format(round((n_projects_metrics['totals']['total']), 2)) , delta=None, delta_color="normal", help=None)

st.write('## Programming')

st.area_chart(data=last_30_days_df, x='Date', y=['sections_programming', 'n_problems'], width=0, height=0, use_container_width=True)

st.write('#### Sections')
sections_programming_metrics = get_display_stats(df, 'sections_programming', False)

sections_programming_total1, sections_programming_total2, sections_programming_total3, sections_programming_total4, sections_programming_total5 = st.columns(5)
sections_programming_total1.metric('This Week','{}'.format(round((sections_programming_metrics['this_week']['total']), 2)) , delta='{}'.format(round(round((sections_programming_metrics['this_week']['total']), 2) - round((sections_programming_metrics['last_week']['total']), 2) )), delta_color="normal", help=None)
sections_programming_total2.metric('Last Week','{}'.format(round((sections_programming_metrics['last_week']['total']), 2)) , delta=None, delta_color="normal", help=None)
sections_programming_total3.metric('This Month','{}'.format(round((sections_programming_metrics['this_month']['total']), 2)) , delta='{}'.format(round(round((sections_programming_metrics['this_month']['total']), 2) - round((sections_programming_metrics['last_month']['total']), 2) )), delta_color="normal", help=None)
sections_programming_total4.metric('Last Month','{}'.format(round((sections_programming_metrics['last_month']['total']), 2)) , delta=None, delta_color="normal", help=None)
sections_programming_total5.metric('Total','{}'.format(round((sections_programming_metrics['totals']['total']), 2)) , delta=None, delta_color="normal", help=None)

st.write('#### Problems')
n_problems_metrics = get_display_stats(df, 'n_problems', False)

n_problems_total1, n_problems_total2, n_problems_total3, n_problems_total4, n_problems_total5 = st.columns(5)
n_problems_total1.metric('This Week','{}'.format(round((n_problems_metrics['this_week']['total']), 2)) , delta='{}'.format(round(round((n_problems_metrics['this_week']['total']), 2) - round((n_problems_metrics['last_week']['total']), 2) )), delta_color="normal", help=None)
n_problems_total2.metric('Last Week','{}'.format(round((n_problems_metrics['last_week']['total']), 2)) , delta=None, delta_color="normal", help=None)
n_problems_total3.metric('This Month','{}'.format(round((n_problems_metrics['this_month']['total']), 2)) , delta='{}'.format(round(round((n_problems_metrics['this_month']['total']), 2) - round((n_problems_metrics['last_month']['total']), 2) )), delta_color="normal", help=None)
n_problems_total4.metric('Last Month','{}'.format(round((n_problems_metrics['last_month']['total']), 2)) , delta=None, delta_color="normal", help=None)
n_problems_total5.metric('Total','{}'.format(round((n_problems_metrics['totals']['total']), 2)) , delta=None, delta_color="normal", help=None)

st.write('## Writing')

st.area_chart(data=last_30_days_df, x='Date', y=['sections_writing', 'n_words'], width=0, height=0, use_container_width=True)

st.write('#### Sections')
sections_writing_metrics = get_display_stats(df, 'sections_writing', False)

sections_writing_total1, sections_writing_total2, sections_writing_total3, sections_writing_total4, sections_writing_total5 = st.columns(5)
sections_writing_total1.metric('This Week','{}'.format(round((sections_writing_metrics['this_week']['total']), 2)) , delta='{}'.format(round(round((sections_writing_metrics['this_week']['total']), 2) - round((sections_writing_metrics['last_week']['total']), 2) )), delta_color="normal", help=None)
sections_writing_total2.metric('Last Week','{}'.format(round((sections_writing_metrics['last_week']['total']), 2)) , delta=None, delta_color="normal", help=None)
sections_writing_total3.metric('This Month','{}'.format(round((sections_writing_metrics['this_month']['total']), 2)) , delta='{}'.format(round(round((sections_writing_metrics['this_month']['total']), 2) - round((sections_writing_metrics['last_month']['total']), 2) )), delta_color="normal", help=None)
sections_writing_total4.metric('Last Month','{}'.format(round((sections_writing_metrics['last_month']['total']), 2)) , delta=None, delta_color="normal", help=None)
sections_writing_total5.metric('Total','{}'.format(round((sections_writing_metrics['totals']['total']), 2)) , delta=None, delta_color="normal", help=None)

st.write('#### Words Total')
n_words_metrics = get_display_stats(df, 'n_words', True)

n_words_total1, n_words_total2, n_words_total3, n_words_total4, n_words_total5 = st.columns(5)
n_words_total1.metric('This Week','{}'.format(round((n_words_metrics['this_week']['total']), 2)) , delta='{}'.format(round(round((n_words_metrics['this_week']['total']), 2) - round((n_words_metrics['last_week']['total']), 2) )), delta_color="normal", help=None)
n_words_total2.metric('Last Week','{}'.format(round((n_words_metrics['last_week']['total']), 2)) , delta=None, delta_color="normal", help=None)
n_words_total3.metric('This Month','{}'.format(round((n_words_metrics['this_month']['total']), 2)) , delta='{}'.format(round(round((n_words_metrics['this_month']['total']), 2) - round((n_words_metrics['last_month']['total']), 2) )), delta_color="normal", help=None)
n_words_total4.metric('Last Month','{}'.format(round((n_words_metrics['last_month']['total']), 2)) , delta=None, delta_color="normal", help=None)
n_words_total5.metric('Total','{}'.format(round((n_words_metrics['totals']['total']), 2)) , delta=None, delta_color="normal", help=None)

st.write('#### Averages per day')
n_words_avg1, n_words_avg2, n_words_avg3, n_words_avg4, n_words_avg5 = st.columns(5)
n_words_avg1.metric('This Week','{}'.format(round((n_words_metrics['this_week']['average']), 2)) , delta='{}'.format(round(round((n_words_metrics['this_week']['average']), 2) - round((n_words_metrics['last_week']['average']), 2) )), delta_color="normal", help=None)
n_words_avg2.metric('Last Week','{}'.format(round((n_words_metrics['last_week']['average']), 2)) , delta=None, delta_color="normal", help=None)
n_words_avg3.metric('This Month','{}'.format(round((n_words_metrics['this_month']['average']), 2)) , delta='{}'.format(round(round((n_words_metrics['this_month']['average']), 2) - round((n_words_metrics['last_month']['average']), 2) )), delta_color="normal", help=None)
n_words_avg4.metric('Last Month','{}'.format(round((n_words_metrics['last_month']['average']), 2)) , delta=None, delta_color="normal", help=None)
n_words_avg5.metric('Total','{}'.format(round((n_words_metrics['totals']['average']), 2)) , delta=None, delta_color="normal", help=None)