import streamlit as st
import pandas as pd # (1)
import numpy as np

import openpyxl, re
import warnings
import calendar
from datetime import datetime
from datetime import timedelta, date

st.title("Drivers Loyalty Program")
emp_uploaded = st.file_uploader("EMPLOYEE data file", type=['xlsx'])
#offDay = st.file_uploader("EMP", type=['xlsx'], key='OffDay')

if emp_uploaded is not None:
    emp = pd.read_excel(emp_uploaded, sheet_name='SalarySummaryPayPeriodReport', engine='openpyxl')
    emp.fillna(0, inplace=True)
    st.write("### Employee Data")
    st.dataframe(emp)

    st.divider()
    offDay = pd.read_excel(emp_uploaded, sheet_name='OffDay', engine='openpyxl')
    offDay.fillna(0, inplace=True)
    st.write("### Employee Off Days")
    st.dataframe(offDay)

def process_dataframe(df):    
    df['Driver'] = df['Driver'].str.replace('(Driver)', '').str.strip() # Remove '(Driver)' from the 'Driver' column  
    df['SN'] = range(1, len(df) + 1) # Add a new column 'SN' with consecutive numbers from 1 to len(df)     
    df['Mark_2'] = 1 # Add a new column 'Mark_2' with all values set to 1       
    df.rename(columns={'Driver': 'NAME'}, inplace=True) # Rename the 'Driver' column to 'NAME'      
    df = df[['SN', 'NAME', 'Completion time', 'Earned', 'Mark_2']] # Reorder columns
    return df

def read_excel_sheets_to_dict(xl_file):
    xlsx = pd.ExcelFile(xl_file)
    sheetNames = xlsx.sheet_names #get names of all worksheets in excel file
    driver_dict = {} #initialize dict
    for sheetName in sheetNames:
        df_0 = pd.read_excel(xl_file, sheet_name=sheetName)
        df = process_dataframe(df_0)

        driver_dict[sheetName] = df
    return driver_dict

xl_uploaded = st.file_uploader("Drivers Trips Data", type=['xlsx'])
if xl_uploaded is not None:
    xl = pd.read_excel(xl_uploaded, engine='openpyxl')
    dct_emp = read_excel_sheets_to_dict(xl_uploaded) #dictionary of driverCode (key) and dataframe (value)

    lst_drivers =[]
    lst_drivers = list(dct_emp)
    for driverCode in lst_drivers:
    
        df_driver = dct_emp[driverCode]
        df_driver.reset_index(drop=True)
    
        col_midnight = ['SN', 'NAME', 'Completion time']
        midnight = df_driver[col_midnight]
        midnight = midnight.reset_index(drop=True)
        st.write(midnight.reset_index(drop=True))
        st.dataframe(df_driver)
