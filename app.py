import streamlit as st
import gspread
import pandas as pd

gc = gspread.service_account_from_dict(st.secrets['gsheet'])
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

df