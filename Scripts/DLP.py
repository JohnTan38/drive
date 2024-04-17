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
#st.markdown("<p style='text-align: center; color: grey;'>"+img_to_html('./image/cars.png')+"</p>", unsafe_allow_html=True)

st.divider()
emp_uploaded = st.file_uploader("EMP data file", type=['xlsx'])

#path_dlp = r"C:/Users/appremote/Documents/DLP/"
#emp = pd.read_excel(path_dlp+ "EMP.xlsx", sheet_name='SalarySummaryPayPeriodReport', engine='openpyxl')
#offDay = pd.read_excel(path_dlp + "EMP.xlsx", sheet_name='OffDay', engine='openpyxl')
if emp_uploaded is not None:
    emp = pd.read_excel(emp_uploaded, sheet_name='SalarySummaryPayPeriodReport', engine='openpyxl')
    col_emp = ['Code', 'NAME', 'JOINING DATE', 'SCHEME']
    emp = emp[col_emp]
    dct_emp = emp.set_index('NAME').to_dict()['Code']
    emp.fillna(0, inplace=True)
    st.write("### Employee Data")
    st.dataframe(emp)

    st.divider()
    offDay = pd.read_excel(emp_uploaded, sheet_name='OffDay', engine='openpyxl')
    col_offDay = ['NAME', 'Code', 'Off Day', 'Driver - Sick Day', 'Driver - Hosp', 'Driver - Workshop']                   
    offDay = offDay[col_offDay]
    offDay.fillna(0, inplace=True)
    st.write("### Employee Off Days")
    st.dataframe(offDay)
st.divider()

def process_dataframe(df):
    try:
        df['Driver'] = df['Driver'].str.replace('(Driver)', '').str.strip() # Remove '(Driver)' from the 'Driver' column
    except:
        df['NAME'] = df['NAME'].str.replace('(Driver)', '').str.strip()
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
        initial_time = pd.to_datetime(lst_midnight[0], format='mixed', dayfirst=True).strftime("%Y-%d-%m")
    #print(initial_time)
    try:
        final_time = pd.to_datetime(parse_date(lst_midnight[-1])) #, format='mixed', dayfirst=True) #.strftime("%Y-%d-%m")
    except Exception as e:
        print(e)
        final_time = pd.to_datetime(lst_midnight[-1], format='mixed', dayfirst=True).strftime("%Y-%d-%m")
    #print(final_time)
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
    #print(count_dates_in_ranges(lst_midnight, lst_tuples_date))

    def Convert(tup, di):
            di = dict(tup)
            return di

    c = {}
    c_sort = Convert(count_dates_in_ranges(lst_midnight, lst_tuples_date), c)
    print(c_sort)
    
    lstDriver.extend([[driverName, driverCode, drive['Mark_2'].sum(), count_non_zero_values(c_sort), totalIncentive, 
                       df_driver['Completion time'].iloc[0]]]) #re.findall('\d+', str(workday.nunique()))[0]
    #print(lstDriver)

Driver = pd.DataFrame(lstDriver, columns=['NAME', 'Code', 'ActualNumber of TripsPerformed', 'Number of DaysWorked', 
                                          'EarnedIncentive', 'FirstWorkingDay'])
mainControl_0 = pd.merge(offDay, Driver, on='Code', how='left')
mainControl = pd.merge(mainControl_0, emp, on='Code', how='inner')
mainControl.drop(columns=['NAME_x', 'NAME_y'])

def int_or_fl(val):
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            pass
    return val #int/float from obj

from calendar import monthrange
import holidays
global str_list_holidays

#yr = 2024
yr = pd.to_datetime(Driver['FirstWorkingDay'].iloc[0]).year
str_list_holidays =[]
list_holidays = list((holidays.SG(years=[yr])).keys())
for holiday in list_holidays:
        str_list_holidays.append(holiday.strftime("%Y-%m-%d"))

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

    lst_completionTime = midnight['Completion time'].tolist() #added 20240416
    lst_date = [parse_date(str(date)) for date in lst_completionTime]
    lst_date_unique = list(set(lst_date))
    lst_date_unique_sorted = sorted(lst_date_unique)

    import datetime as dt
    try:
        initial_time = pd.to_datetime(parse_date(lst_midnight[0])) #.strftime("%Y-%d-%m")
    except Exception as e:
        print(e)
        initial_time = pd.to_datetime((lst_midnight[0]), format='mixed', dayfirst=True).strftime("%Y-%m-%d")
    #print(initial_time)
    try:
        final_time = pd.to_datetime(parse_date(lst_midnight[-1])) #, format='mixed', dayfirst=True) #.strftime("%Y-%m-%d")
    except Exception as e:
         print(e)
         final_time = pd.to_datetime((lst_midnight[-1]), format='mixed', dayfirst=True).strftime("%Y-%m-%d")
    #print(final_time)
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
    #print(count_dates_in_ranges(lst_midnight, lst_tuples_date))

    def Convert(tup, di):
            di = dict(tup)
            return di

    c = {}
    c_sort = Convert(count_dates_in_ranges(lst_midnight, lst_tuples_date), c)
    c_sort_1 = c_sort
    print(c_sort_1)
    #c = collections.Counter(lst_trip_cnt)
    #c_sort = dict(sorted(c.items(), key=lambda item: item[0])) #sort keys

    def get_values(dct):
        return list(dct.values()) #20240417
    list_number_of_trips = get_values(c_sort) #list of number of trips for each day
    print(list_number_of_trips)

    lst_tripIncentive =[] ##

    for key, value in c_sort.items():
        q,mod = divmod(value, 7)
                
        if value >7:
            #tripIncentive = ((q-1)*7 + mod)*2
            tripIncentive = 2
            lst_tripIncentive.append(tripIncentive)         
        else:
            tripIncentive = 0
            lst_tripIncentive.append(tripIncentive)

    #sum_tripIncentive = sum(lst_tripIncentive)
    #print('sum_tripIncentive= '+str(sum_tripIncentive))
    #lst_sum_driverIncentive.extend([[midnightDriver, sum_tripIncentive]])

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
    #print(lst_date_unique_sorted)

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

    def list_remove_duplicates_preserve_order(lst):
        seen = set()
        seen_add = seen.add
        return [x for x in lst if not (x in seen or seen_add(x))]
    str_date_unique_sorted = list_remove_duplicates_preserve_order(str_date_unique_sorted)
    #print(str_date_unique_sorted) #20240417
        

    lst_incentive_PublicHoliday =[]
    for ele in str_date_unique_sorted:
            idx = str_date_unique_sorted.index(ele)
            try:
                 
                if ele in str_list_holidays and list(c_sort_1.values())[idx]>0:
                    #if pd.to_datetime(ele).weekday() ==6:
                    incentive_PublicHoliday = 40 #work on a public holiday & trips>0                          
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
             
            if pd.to_datetime(ele).weekday() ==6 and list(c_sort_1.values())[idx]>0:
                incentive_Sunday = 40 #work on Sunday & trips>0        
            elif pd.to_datetime(ele).weekday() ==6:
                incentive_Sunday = 20            
            else:
                incentive_Sunday = 0
        except Exception as e:
            print(e)
        lst_incentive_Sunday.append(incentive_Sunday)
    #print(lst_incentive_Sunday)

    #Sunday trip incentive is $12
    def divide_by_multiple_of_eight(lst):
        quotients = []
        for num in lst:
            # Find the highest multiple of 8 that is less than or equal to num
            highest_multiple = (num // 8)
            # If the highest multiple is 0, it means num is less than 8, so we set the highest multiple to 1 to avoid division by zero
            if highest_multiple == 0:
                quotient = 0
            quotient = highest_multiple*2
            quotients.append(quotient)
        return quotients

    list_incentive_trips = divide_by_multiple_of_eight(list_number_of_trips)
    print('list_incentive_trips')
    print(list_incentive_trips)
   

    def calculate_incentive_sunday(list_incentive_Sunday, list_incentive_trips):
        list_incentive_sundayTrips = []
        for i in range(len(list_incentive_Sunday)):
            if (list_incentive_Sunday[i] == 40 or list_incentive_Sunday[i] == 20) and list_incentive_trips[i] != 0:
                incentive_sunday_trip = 6 * list_incentive_trips[i]
            else:
                incentive_sunday_trip = 0
            list_incentive_sundayTrips.append(incentive_sunday_trip)
            #print(list_incentive_sundayTrips)
        return list_incentive_sundayTrips #20240417
    lst_incentive_Sundays = calculate_incentive_sunday(lst_incentive_Sunday, list_incentive_trips)
    #print(lst_incentive_Sundays)

    def calculate_incentive_nonSunday(list_incentive_Sunday, list_incentive_trips):
        list_incentive_nonSundayTrips = []
        for i in range(len(list_incentive_Sunday)):
            if list_incentive_Sunday[i] == 0 and list_incentive_trips[i] != 0:
                incentive_nonSunday_trip = 1 * list_incentive_trips[i]
            else:
                incentive_nonSunday_trip = 0
            list_incentive_nonSundayTrips.append(incentive_nonSunday_trip)
            #print(list_incentive_nonSundayTrips)
        return list_incentive_nonSundayTrips #20240417
    lst_incentive_nonSundayTrips = calculate_incentive_nonSunday(lst_incentive_Sunday, list_incentive_trips)
    print('lst_incentive_nonSundayTrips')
    print(lst_incentive_nonSundayTrips)
    sum_tripIncentive = sum(lst_incentive_nonSundayTrips)
    lst_sum_driverIncentive.extend([[midnightDriver, sum_tripIncentive]]) ##
       
    lst_incentive_MondayHoliday =[]
    for ele in str_date_unique_sorted:
        idx = str_date_unique_sorted.index(ele)
        try:
             
            if pd.to_datetime(ele).weekday() ==0 and (pd.to_datetime(ele) - timedelta(days=1)) in str_list_holidays and list(c_sort.values())[idx]>0:
                    incentive_MondayHoliday = 40 #work on Monday (Sunday holiday) & trips>5
            elif pd.to_datetime(ele).weekday() ==0 and (pd.to_datetime(ele) - timedelta(days=1)) in str_list_holidays:
                    incentive_MondayHoliday = 20
            else:
                    incentive_MondayHoliday = 0
        except Exception as e:
            print(e)
        lst_incentive_MondayHoliday.append(incentive_MondayHoliday)
    #print(lst_incentive_MondayHoliday)
    
    holiday_incentive.extend([[midnightDriver, sum(lst_incentive_PublicHoliday), sum(lst_incentive_Sundays), 
                               sum(lst_incentive_MondayHoliday) ]])

driversIncentive = pd.DataFrame(lst_sum_driverIncentive, columns=['NAME', 'TotalTripsIncentive'])
holidaysIncentive = pd.DataFrame(holiday_incentive, columns=['NAME', 'PublicHolidayIncentive', 'SundayIncentive', 
                                                             'MondayHolidayIncentive'])

print(count_non_zero_values(c_sort)) #number of working days where trips are made


Incentive = pd.merge(driversIncentive, holidaysIncentive, on='NAME', how='outer') # (3a)
Incentive.rename(columns={'NAME': 'Code'}, inplace=True)
incentiveFinal = pd.merge(mainControl_1.drop(columns=['NAME_x', 'NAME_y']), Incentive, on='Code', how='outer')

cols_add = ['TotalTripsIncentive', 'PublicHolidayIncentive', 'SundayIncentive', 'MondayHolidayIncentive']
incentiveFinal['GrandTotal_Incentive'] = incentiveFinal[cols_add].sum(axis=1)
col_final = ['NAME', 'Code', 'ActualNumber of TripsPerformed', 'Number of DaysWorked', 'Off Day', 
             'Driver - Sick Day', 'Driver - Hosp', 'Driver - Workshop', 'FinalWorkingDay', 'TotalTrips', 'SCHEME', 
             'GrandTotal_Incentive', 'TotalTripsIncentive', 'PublicHolidayIncentive', 'SundayIncentive', 'MondayHolidayIncentive', 
             'DLP', 'JOINING DATE', 'ServiceYear', 'DLP Amount']
incentiveFinal = incentiveFinal[col_final]
incentiveFinal = incentiveFinal.drop_duplicates()

if incentiveFinal is not None:
    st.write("### Driver Incentive DataTable")
    st.dataframe(incentiveFinal)
