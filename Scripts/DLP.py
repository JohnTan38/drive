import streamlit as st
import pandas as pd # (1)
import numpy as np

import openpyxl, re
import warnings
import calendar
from datetime import datetime
from datetime import timedelta, date

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_colwidth', None)
pd.set_option('mode.chained_assignment', None)


st.set_page_config(page_title="DLP", page_icon="🚗", layout="wide")

st.markdown("<h1 style='text-align: center; color: black;'>Driver Loyalty Program</h1>", unsafe_allow_html=True)
#st.title("Drivers Loyalty Program")
import base64
from pathlib import Path
def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded
def img_to_html(img_path):
    img_html = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(
      img_to_bytes(img_path)
    )
    return img_html
st.markdown("<p style='text-align: center; color: grey;'>"+img_to_html('./image/cars.png')+"</p>", unsafe_allow_html=True)

st.divider()
emp_url = 'https://raw.githubusercontent.com/JohnTan38/agi/main/docs/EMP.xlsx'
#emp_uploaded = st.file_uploader("EMPLOYEE data file", type=['xlsx'])
emp_uploaded = pd.read_excel(emp_url, engine='openpyxl')

#emp = pd.read_excel(path_dlp+ "EMP.xlsx", sheet_name='SalarySummaryPayPeriodReport', engine='openpyxl')
#offDay = pd.read_excel(path_dlp + "EMP.xlsx", sheet_name='OffDay', engine='openpyxl')
if emp_uploaded is not None:
    emp = pd.read_excel(emp_url, sheet_name='SalarySummaryPayPeriodReport', engine='openpyxl')
    col_emp = ['Code', 'NAME', 'JOINING DATE', 'SCHEME']
    emp = emp[col_emp]
    dct_emp = emp.set_index('NAME').to_dict()['Code']
    emp.fillna(0, inplace=True)
    st.write("### Employee Data")
    st.dataframe(emp)

    st.divider()
    offDay = pd.read_excel(emp_url, sheet_name='OffDay', engine='openpyxl')
    col_offDay = ['NAME', 'Code', 'Off Day', 'Driver - Sick Day', 'Driver - Hosp', 'Driver - Workshop']                   
    offDay = offDay[col_offDay]
    offDay.fillna(0, inplace=True)
    st.write("### Employee Off Days")
    st.dataframe(offDay)
st.divider()

def process_dataframe(df):    
    df['NAME'] = df['NAME'].str.replace('(Driver)', '').str.strip() # Remove '(Driver)' from the 'Driver' column  
    df['SN'] = range(1, len(df) + 1) # Add a new column 'SN' with consecutive numbers from 1 to len(df)     
    df['Mark_2'] = 1 # Add a new column 'Mark_2' with all values set to 1       
    df.rename(columns={'Driver': 'NAME'}, inplace=True) # Rename the 'Driver' column to 'NAME'      
    df = df[['SN', 'NAME', 'Completion time', 'Earned', 'Mark_2']] # Reorder columns
    return df


#read excel file and return a dictionary of sheet names and dataframes
def read_excel_sheets_to_dict(xl_file):
    xlsx = pd.ExcelFile(xl_file)
    sheetNames = xlsx.sheet_names #get names of all worksheets in excel file
    driver_dict = {} #initialize dict
    for sheetName in sheetNames:
        df_0 = pd.read_excel(xl_file, sheet_name=sheetName)
        df = process_dataframe(df_0)
        driver_dict[sheetName] = df
    return driver_dict

lstDLP = []
#lst_Alldrivers = emp['Code'].tolist()
#lst_drivers = np.unique(np.array(lst_Alldrivers)) #unique values in a list
#xl = pd.ExcelFile(path_dlp+'undefined_3.xlsx')
lst_drivers = []
lstDriver = []

xl_uploaded = st.file_uploader("Drivers Trips Data", type=['xlsx'])
if xl_uploaded is not None:
    xl = pd.read_excel(xl_uploaded, engine='openpyxl')
    dct_emp = read_excel_sheets_to_dict(xl_uploaded) #dictionary of driverCode (key) and dataframe (value)
    lst_drivers = list(dct_emp) #dict keys as list
    for driverCode in lst_drivers:
        df_driver = dct_emp[driverCode]
        df_driver.reset_index(drop=True)

#for driver in xl.sheet_names:
    #emp_0 = dct_emp.get(driver)
    #lst_drivers.append(emp_0)

def parse_date(date_string):
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S'):
             try:
                 return datetime.strptime(date_string, fmt)#.date()
             except ValueError:
                 pass
        raise ValueError('no valid date format found')
def count_dates_in_ranges(list_dates, list_of_tuples):
    try:
        list_dates = [parse_date(str(date)) for date in list_dates] # Convert all dates to datetime objects
    except Exception as e:
        print(e)
    
    list_of_tuples = [(datetime.strptime(str(start), '%Y-%m-%d %H:%M:%S'), datetime.strptime(str(end), '%Y-%m-%d %H:%M:%S')) for start, end in list_of_tuples]

    counters = [0] * len(list_of_tuples) # Initialize a list of counters

    for date in list_dates:
        for i, (start, end) in enumerate(list_of_tuples):
            # Check if date is within the range and increment the corresponding counter if true
            if start <= date < end:
                counters[i] += 1

    # Create a list of tuples (counter i: count)
    result = [(f'day {i+1}', count) for i, count in enumerate(counters)]
    return result

def count_non_zero_values(dct):
     count = sum(1 for value in dct.values() if value !=0) #count number of keys with non-zero values
     return count

for driverCode in lst_drivers:
    #df_driver = pd.read_excel(xl_uploaded, sheet_name=driverCode, engine='openpyxl')
    df_driver = dct_emp[driverCode] #get dict values with key

    col_drive = ['Mark_2'] #total number of trips performed
    drive = df_driver[col_drive]
    drive['Mark_2'] = drive[col_drive].apply(pd.to_numeric, errors='coerce') #convert cols to numeric
    drive['Mark_2'] = np.where(drive['Mark_2'] == 'NA', [0], drive['Mark_2']) #replace blank cells with 0
    #driver = driver.groupby(['Quantity']).size().reset_index(name='Count') #count no. of rows with same value
    col_workday = ['Completion time'] #number of days worked
    workday = df_driver[col_workday]
    workday.drop_duplicates(['Completion time'], inplace=True)
    workday = workday[workday['Completion time'].notna()]
    workday['Completion time'] = pd.to_datetime(workday['Completion time'], format='mixed', dayfirst=True).dt.strftime('%Y-%m-%d')
    workday.drop_duplicates(['Completion time'], inplace=True)
    workday.reset_index(drop=True, inplace=True)

    driverName = df_driver.loc[0, 'NAME']
    col_incentive = ['Earned']
    incentive = df_driver[col_incentive].astype(float).dropna()
    totalIncentive = incentive['Earned'].sum()


    #midnight = pd.read_excel(xl_uploaded, sheet_name=driverCode, engine='openpyxl')
    col_midnight = ['SN', 'NAME', 'Completion time']
    midnight = df_driver[col_midnight]
    midnight.reset_index(drop=True, inplace=True)

    dct_midnight = midnight.set_index('SN').to_dict()['Completion time']
    lst_midnight = midnight['Completion time'].tolist()

    import datetime as dt
    try:
        initial_time = pd.to_datetime(parse_date(lst_midnight[0]))#, format='mixed', dayfirst=True) #.strftime("%Y-%d-%m")
    except Exception as e:
        print(e)
    print(initial_time)
    try:
        final_time = pd.to_datetime(parse_date(lst_midnight[-1])) #, format='mixed', dayfirst=True) #.strftime("%Y-%d-%m")
    except Exception as e:
        print(e)
    print(final_time)
    numbr_of_days = (pd.to_datetime(final_time) - pd.to_datetime(initial_time)).days #number of days
    lst_start_date = []
    lst_end_date = []
    h=12
    hh=36

    for i in range(numbr_of_days+1):
        startTime = pd.to_datetime(initial_time) + timedelta(hours=h)
        lst_start_date.append(startTime)
        endTime = pd.to_datetime(initial_time) + timedelta(hours=hh)
        lst_end_date.append(endTime)
        h=h+24
        hh=hh+24

    lst_tuples_date = list(zip(lst_start_date, lst_end_date)) # Use zip to create tuples and convert to a list
    print(count_dates_in_ranges(lst_midnight, lst_tuples_date))

    def Convert(tup, di):
            di = dict(tup)
            return di

    c = {}
    c_sort = Convert(count_dates_in_ranges(lst_midnight, lst_tuples_date), c)
    #print(c_sort)
    
    lstDriver.extend([[driverName, driverCode, drive['Mark_2'].sum(), count_non_zero_values(c_sort), totalIncentive, 
                       df_driver['Completion time'].iloc[0]]]) #re.findall('\d+', str(workday.nunique()))[0]
    #print(lstDriver)

Driver = pd.DataFrame(lstDriver, columns=['NAME', 'Code', 'ActualNumber of TripsPerformed', 'Number of DaysWorked', 
                                          'EarnedIncentive', 'FirstWorkingDay'])
from calendar import monthrange
import holidays
global str_list_holidays

def int_or_fl(val):
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            pass
    return val #int/float from obj

def holiday_in_month(start,end):
    #str_list_holidays = []
    str_d =[]
    d = pd.date_range(start=start, end=end)
    for dat in d:
          str_d.append(dat.strftime("%Y-%m-%d"))
    return sum(y in str_list_holidays for y in str_d)

def businessDays(year, month):
    days = monthrange(year, month)[1]
    list_businessDay =[]
    for day in range(1, days+1):
        a = datetime(year, month, day)
        if a.weekday()<6:
            list_businessDay.append(str(a))
    return len(list_businessDay)

def first_date_of_month(year, month):
    """Return the first date of the month.
    Args:
        year (int): Year
        month (int): Month

    Returns:
        date (datetime): First date of the current month
    """
    first_date = datetime(year, month, 1)
    return first_date.strftime("%Y-%m-%d")

def last_date_of_month(year, month):
    """Return the last date of the month.
    Args:
        year (int): Year, i.e. 2022
        month (int): Month, i.e. 1 for January

    Returns:
        date (datetime): Last date of the current month
    """
    if month == 12:
        last_date = datetime(year, month, 31)
    else:
        last_date = datetime(year, month + 1, 1) + timedelta(days=-1)
    return last_date.strftime("%Y-%m-%d")

global mainControl_1
if st.button("Get MainControl"):
    mainControl_0 = pd.merge(offDay, Driver, on='Code', how='left')
    mainControl = pd.merge(mainControl_0, emp, on='Code', how='inner')
    mainControl.drop(columns=['NAME_x', 'NAME_y'])

    yr = 2024
    #yr = pd.to_datetime(Driver['FirstWorkingDay'].iloc[0]).year
    str_list_holidays =[]
    list_holidays = list((holidays.SG(years=[yr])).keys())
    for holiday in list_holidays:
            str_list_holidays.append(holiday.strftime("%Y-%m-%d"))


    col_numeric = ['Number of DaysWorked', 'Off Day', 'Driver - Sick Day', 'Driver - Hosp', 'Driver - Workshop']
    col_numeric_trip = ['Off Day', 'Driver - Sick Day', 'Driver - Hosp', 'Driver - Workshop']
    mainControl[col_numeric] = mainControl[col_numeric].apply(pd.to_numeric, errors='coerce') #convert cols to numeric
    mainControl['FinalWorkingDay'] = mainControl[col_numeric].sum(axis=1, numeric_only=True) #sum multiple cols

    mainControl['NoWorkTrip'] = mainControl[col_numeric_trip].sum(axis=1, numeric_only=True)
    mainControl['TotalTrips'] = mainControl['ActualNumber of TripsPerformed'] + (mainControl['NoWorkTrip'])*8
    mainControl = mainControl.dropna(subset=['Number of DaysWorked'])
    mainControl = mainControl.reset_index(drop=True)

    for i in range(len(mainControl)):
        #print(i)
        driverCode = mainControl.loc[i,'Code']
        nationality = mainControl[mainControl['Code']==driverCode]['SCHEME'].values[0]
        firstWorkingDay = mainControl.loc[mainControl['Code']==driverCode, 'FirstWorkingDay'].values[0]
        yr = pd.to_datetime(firstWorkingDay).year
        mth = pd.to_datetime(firstWorkingDay).month
        start = first_date_of_month(yr, mth)
        end = last_date_of_month(yr, mth)
        numbr_WorkingDays = businessDays(yr, mth) + holiday_in_month(start,end)

        if nationality == 'LOC':
                finalWorkingDay = mainControl['FinalWorkingDay'][i].astype(int)
                hireDate = pd.to_datetime(mainControl['JOINING DATE'][i], dayfirst=True)
                serviceYears = (pd.to_numeric((datetime.now() - hireDate).days, downcast='integer') / 365.25)
                serviceYear = round(serviceYears, 2)
            
                totalTrip = int_or_fl(mainControl['TotalTrips'][i])
                actualTrip = int_or_fl(mainControl['ActualNumber of TripsPerformed'][i])
                driverName = mainControl['NAME'][i]
                if finalWorkingDay > numbr_WorkingDays and totalTrip >= finalWorkingDay*8:
                    lstDLP.extend([[driverName, serviceYear, '300', 'Yes']])
                else:
                    lstDLP.extend([[driverName, serviceYear, '-', 'No']])
    
        if nationality == 'TPT':
                finalWorkingDay = mainControl['FinalWorkingDay'][i].astype(int)
                hireDate = pd.to_datetime(mainControl['JOINING DATE'][i], dayfirst=True)
                serviceYears = (pd.to_numeric((datetime.now() - hireDate).days, downcast='integer') / 365.25)
                serviceYear = round(serviceYears, 2)
            
                totalTrip = int_or_fl(mainControl['TotalTrips'][i])
                actualTrip = int_or_fl(mainControl['ActualNumber of TripsPerformed'][i])
                driverName = mainControl['NAME'][i]
                if serviceYear >=5 and finalWorkingDay > numbr_WorkingDays and totalTrip >= finalWorkingDay*8:
                    lstDLP.extend([[driverName, serviceYear, '300', 'Yes']])
                elif serviceYear <5 and serviceYear >= 2 and finalWorkingDay > numbr_WorkingDays and totalTrip >= finalWorkingDay*8:
                    lstDLP.extend([[driverName, serviceYear, '100', 'Yes']])
                else:
                    lstDLP.extend([[driverName, serviceYear, '-', 'No']])
    
        if nationality == 'PRC' or nationality == 'BL':
                lstDLP.extend([[driverName, '-', '-', 'No']])

    dfDLP = pd.DataFrame(lstDLP, columns=['NAME', 'ServiceYear', 'DLP Amount', 'DLP']) #df from list of lists
    mainControl_1 = (pd.merge(mainControl, dfDLP, on='NAME', how='left')).drop(['NoWorkTrip'], axis=1, errors='ignore')
    mainControl_1[['Driver - Sick Day', 'Driver - Hosp', 'Driver - Workshop']] = mainControl_1[['Driver - Sick Day', 
                                                                                                    'Driver - Hosp', 
                                                                                                    'Driver - Workshop']].fillna('-')
    mainControl_1.drop(columns=['NAME_x', 'NAME_y'])
    st.write('Please download and save as MAIN_CONTROL.csv')
    st.dataframe(mainControl_1, use_container_width=True)

#2
import itertools
import collections

lst_sum_driverIncentive =[]
holiday_incentive =[]

def count_dates_in_ranges(list_dates, list_of_tuples):
    try:
        list_dates = [parse_date(str(date)) for date in list_dates] # Convert all dates to string
    except AttributeError as e:
        print(e)
    
    list_of_tuples = [(datetime.strptime(str(start), '%Y-%m-%d %H:%M:%S'), datetime.strptime(str(end), '%Y-%m-%d %H:%M:%S')) for start, end in list_of_tuples]

    counters = [0] * len(list_of_tuples) # Initialize a list of counters

    for date in list_dates:
        for i, (start, end) in enumerate(list_of_tuples):
            # Check if date is within the range and increment the corresponding counter if true
            if start <= date < end:
                counters[i] += 1

    # Create a list of tuples (counter i: count)
    result = [(f'day {i+1}', count) for i, count in enumerate(counters)]
    return result

def isNowinTimePeriod(startTime, endTime, nowTime):
    if startTime < endTime:
        return nowTime >= startTime and nowTime <= endTime
    else:
        return nowTime >= startTime or nowTime <= endTime #over midnight

def count_non_zero_values(dct):
     count = sum(1 for value in dct.values() if value !=0) #count number of keys with non-zero values
     return count


lst_midnightDrivers = lst_drivers

for midnightDriver in lst_midnightDrivers:
    midnight = pd.read_excel(xl_uploaded, sheet_name=midnightDriver, engine='openpyxl')
    midnight = process_dataframe(midnight)
    col_midnight = ['SN', 'NAME', 'Completion time']
    midnight = midnight[col_midnight]
    midnight = midnight.reset_index(drop=True, inplace=False)

    dct_midnight = midnight.set_index('SN').to_dict()['Completion time']
    lst_midnight = midnight['Completion time'].tolist()

    import datetime as dt
    initial_time = pd.to_datetime(parse_date(lst_midnight[0])) #.strftime("%Y-%d-%m")
    print(initial_time)
    final_time = pd.to_datetime(parse_date(lst_midnight[-1])) #, format='mixed', dayfirst=True) #.strftime("%Y-%m-%d")
    print(final_time)
    numbr_of_days = (pd.to_datetime(final_time) - pd.to_datetime(initial_time)).days #number of days
    lst_start_date = []
    lst_end_date = []
    h=12
    hh=36

    for i in range(numbr_of_days+1):
        startTime = pd.to_datetime(initial_time) + timedelta(hours=h)
        lst_start_date.append(startTime)
        endTime = pd.to_datetime(initial_time) + timedelta(hours=hh)
        lst_end_date.append(endTime)
        h=h+24
        hh=hh+24

    lst_tuples_date = list(zip(lst_start_date, lst_end_date)) # Use zip to create tuples and convert to a list
    print(count_dates_in_ranges(lst_midnight, lst_tuples_date))

    def Convert(tup, di):
            di = dict(tup)
            return di

    c = {}
    c_sort = Convert(count_dates_in_ranges(lst_midnight, lst_tuples_date), c)
    print(c_sort)
    #c = collections.Counter(lst_trip_cnt)
    #c_sort = dict(sorted(c.items(), key=lambda item: item[0])) #sort keys
    lst_tripIncentive =[]

    for key, value in c_sort.items():
        q,mod = divmod(value, 7)
                
        if value >7:
            tripIncentive = ((q-1)*7 + mod)*2
            lst_tripIncentive.append(tripIncentive)            
        else:
            tripIncentive = 0
            lst_tripIncentive.append(tripIncentive)

    sum_tripIncentive = sum(lst_tripIncentive)
    lst_sum_driverIncentive.extend([[midnightDriver, sum_tripIncentive]])

    def parse_date(date_string):
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S'):
             try:
                 return datetime.strptime(date_string, fmt)#.date()
             except ValueError:
                 pass
        raise ValueError('no valid date format found')
    
    #lst_trip_cnt
    lst_completionTime = midnight['Completion time'].tolist()
    lst_date = [parse_date(str(date)) for date in lst_completionTime]
    lst_date_unique = list(set(lst_date))
    lst_date_unique_sorted = sorted(lst_date_unique)

    lst_day = [calendar.day_name[date.weekday()] for date in lst_date_unique_sorted]
    lst_dayNum = [date.strftime('%w') for date in lst_date_unique_sorted]

    from datetime import date
    import holidays

    yr = pd.to_datetime(lst_completionTime[0]).year
    #list((holidays.SG(years=[2021])).keys())
    str_list_holidays =[]
    list_holidays = list((holidays.SG(years=[yr])).keys())
    for holiday in list_holidays:
        str_list_holidays.append(holiday.strftime("%Y-%m-%d"))
    
    str_date_unique_sorted =[]
    for date in lst_date_unique_sorted:
        str_date_unique_sorted.append(date.strftime("%Y-%m-%d"))
    
    lst_incentive_PublicHoliday =[]
    for ele in str_date_unique_sorted:
            idx = str_date_unique_sorted.index(ele)
            try:
                 
                if ele in str_list_holidays and list(c_sort.values())[idx]>5:
                    #if pd.to_datetime(ele).weekday() ==6:
                    incentive_PublicHoliday = 40 #work on a public holiday & trips>5                            
                elif ele in str_list_holidays:
                    incentive_PublicHoliday = 20                
                else:
                    incentive_PublicHoliday = 0
            except Exception as e:
                 print(e)
            lst_incentive_PublicHoliday.append(incentive_PublicHoliday)
    #print(lst_incentive_PublicHoliday)
    
    lst_incentive_Sunday =[]
    for ele in str_date_unique_sorted:
        idx = str_date_unique_sorted.index(ele)
        try:
             
            if pd.to_datetime(ele).weekday() ==0 and list(c_sort.values())[idx]>5:
                incentive_Sunday = 40 #work on Sunday & trips>5        
            elif pd.to_datetime(ele).weekday() ==0:
                incentive_Sunday = 20            
            else:
                incentive_Sunday = 0
        except Exception as e:
            print(e)
        lst_incentive_Sunday.append(incentive_Sunday)
    #print(lst_incentive_Sunday)
        
    lst_incentive_MondayHoliday =[]
    for ele in str_date_unique_sorted:
        idx = str_date_unique_sorted.index(ele)
        try:
             
            if pd.to_datetime(ele).weekday() ==0 and (pd.to_datetime(ele) - timedelta(days=1)) in str_list_holidays and list(c_sort.values())[idx]>5:
                    incentive_MondayHoliday = 40 #work on Monday (Sunday holiday) & trips>5
            elif pd.to_datetime(ele).weekday() ==0 and (pd.to_datetime(ele) - timedelta(days=1)) in str_list_holidays:
                    incentive_MondayHoliday = 20
            else:
                    incentive_MondayHoliday = 0
        except Exception as e:
            print(e)
        lst_incentive_MondayHoliday.append(incentive_MondayHoliday)
   
    holiday_incentive.extend([[midnightDriver, sum(lst_incentive_PublicHoliday), sum(lst_incentive_Sunday), 
                               sum(lst_incentive_MondayHoliday) ]])

driversIncentive = pd.DataFrame(lst_sum_driverIncentive, columns=['NAME', 'TotalTripsIncentive'])
holidaysIncentive = pd.DataFrame(holiday_incentive, columns=['NAME', 'PublicHolidayIncentive', 'SundayIncentive', 
                                                             'MondayHolidayIncentive'])

#print(count_non_zero_values(c_sort)) #number of working days where trips are made

Incentive = pd.merge(driversIncentive, holidaysIncentive, on='NAME', how='outer') # (3a)
Incentive.rename(columns={'NAME': 'Code'}, inplace=True)

mainControl_uploaded = st.file_uploader("MAIN_CONTROL", type=['csv'])

if st.button('Get Incentive'):
    mainControl_2 = pd.read_excel(mainControl_uploaded, engine='openpyxl')
    incentiveFinal = pd.merge(mainControl_2.drop(columns=['NAME_x', 'NAME_y']), Incentive, on='Code', how='outer')

    cols_add = ['TotalTripsIncentive', 'PublicHolidayIncentive', 'SundayIncentive', 'MondayHolidayIncentive']
    incentiveFinal['GrandTotal_Incentive'] = incentiveFinal[cols_add].sum(axis=1)
    col_final = ['NAME', 'Code', 'ActualNumber of TripsPerformed', 'Number of DaysWorked', 'Off Day', 
                 'Driver - Sick Day', 'Driver - Hosp', 'Driver - Workshop', 'FinalWorkingDay', 'TotalTrips', 'SCHEME', 
                 'GrandTotal_Incentive', 'TotalTripsIncentive', 'PublicHolidayIncentive', 'SundayIncentive', 'MondayHolidayIncentive', 
                 'DLP', 'JOINING DATE', 'ServiceYear', 'DLP Amount']
    incentiveFinal = incentiveFinal[col_final]

    if incentiveFinal is not None:
        st.write("### Driver Incentive DataTable")
        st.dataframe(incentiveFinal)
