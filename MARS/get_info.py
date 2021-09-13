#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import pandas as pd
import numpy as np
import datetime as dt

def date_of_birth(datadir, file_list):
    for file in file_list: 
        if file[-7:].lower()=='dob.csv':
            if file[0]!=".":
                demographics = datadir + "/" + file
    demo = pd.DataFrame(pd.read_csv(demographics, on_bad_lines='skip'))
    demo = demo.dropna(how='all')
    demo['id'] = demo['id'].astype(str)
    demo.columns = demo.columns.str.lower()
    demo['dob'] = pd.to_datetime(demo['dob']).dt.strftime("%m/%d/%Y")
    return demo

# Can I make these part of agd_to_csv function
def read_accel_csv(demo, file, record_id):
    df = pd.read_csv(open(file), engine='python', skiprows=10, on_bad_lines='skip')    # Read accelerometer data
    df.insert(loc=0, column='month', value=record_id[0])    # Add month from record name
    df.insert(loc=1, column='id', value=record_id[1:len(record_id)])    # Add id from record name
    df['id'] = df['id'].astype(str)    # Change id to integer to allow date of birth merge
    df = pd.merge(demo, df, on='id', how='inner')    # Merge date of birth data
    df.columns = df.columns.str.replace(' ', '')    # Remove all spaces from variable names
    df.columns = df.columns.str.lower()    # Change all columns to lower case
    df = df.rename(columns = {"vectormagnitude": "vector_magnitude"})    # Rename vector magnitude
    try:
        df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y')
    except:
        df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y')
    df.insert(loc=2, column='age', value=np.floor(((pd.to_datetime(df['date']) - pd.to_datetime(df['dob'])).dt.days) / 365.25).astype(int))        
    df = df[['month', 'id', 'date', 'time', 'age', 'axis1', 'vector_magnitude']].sort_values(['date', 'time'])
    df['study_day'] = dt.datetime.strftime(df['date'][0], '%m/%d/%Y')
    df['study_day'] = ((pd.to_datetime(df['date']) - pd.to_datetime(df['study_day'])).dt.days) + 1
    df = df[df['study_day'] <= 7]
    return df

def season(x):
    spring = range(78, 171)
    summer = range(171, 265)
    fall = range(265, 355)
    if x in spring:
        return 'Spring'
    if x in summer:
        return 'Summer'
    if x in fall:
        return 'Fall'
    else:
        return 'Winter'

def day_of_the_week(date):
    day_of_the_week = pd.to_datetime(date).dt.strftime('%A')
    return day_of_the_week

def time_of_the_day(time):
    time_of_the_day = pd.cut(pd.to_datetime(time).dt.hour,
                            bins = [0, 9, 15, 19, 24],
                            right = False,
                            labels = ["1. 12 am to 9 am", "2. 9 am to 3 pm", "3. 3 pm to 7 pm", "4. After 7 pm"]).astype(str)
    return time_of_the_day
    
   
