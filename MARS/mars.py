#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Set these parameters before executing Python Script
study = "kuccsp"
study_id = "AKUCCSP01" # Example of a study ID
datadir = "/Users/bhelsel/Desktop/Test/AGD60"
adult_cp = "troiano_adult"
child_cp = ""
axis = 1
valid = 480
tol = 2
bout = 10


# Import Libraries
import pandas as pd
import numpy as np
import os
import time
import datetime as dt
import cutpoints as cp
import wear_validation as wv
import agd_to_csv as agd
import get_info as gt

# Start timer
start_time = time.time()

# Set directory and retreive files
os.chdir(datadir)
files = sorted(os.listdir())


# Retreive Date of Birth from Participants
demo = gt.date_of_birth(datadir = datadir, file_list = files)


# Convert AGD Files to CSV Format
newdatadir = agd.to_csv(datadir)


# Read in the list of CSV files
os.chdir(newdatadir)
files = sorted(os.listdir())
csv_files = [file for file in files if file[-4:].lower()=='.csv' and file[0]!="."]


# Create an empty dataframe to append accelerometer data
accel_data = pd.DataFrame()


# Loop through accelerometer csv files
for file in csv_files:        
    
    # Data Processing
    
    record_id = file[0:len(study_id)]
    print("Processing accelerometer data from: " + record_id)
    df = gt.read_accel_csv(demo, file, record_id)
    df['season'] = pd.DatetimeIndex(df['date']).dayofyear.map(gt.season)
    df['day_of_the_week'] = gt.day_of_the_week(df['date'])
    df['time_of_the_day'] = gt.time_of_the_day(df['time'])
    
    # Classify intensity based on set cut-points from the cutpoints.py file.
    df_under18 = df[df['age'] < 18].reset_index(drop=True)
    df_18over = df[df['age'] >= 18].reset_index(drop=True)
    if child_cp != "":
        df_under18, cur_set_child = cp.cut_points(df_under18, set_name = child_cp, n_axis = axis)
    if adult_cp != "":
        df_18over, cur_set_adult = cp.cut_points(df_18over, set_name = adult_cp, n_axis = axis)    
    df = pd.concat([df_under18, df_18over]).sort_values(by=['month', 'id', 'date', 'time']).reset_index(drop=True)
    
    # Detect MVPA bouts
    df = cp.detect_bouts(data = df, bout = bout, tol = tol)
    
    # Detect malfucntion (suprious ≥ 20,000 cpm or no change for 10 min. at value > 0)
    df = wv.detect_malfunction(df)
    
    # Detect valid and nonwear time (≥ 60 min. of 0 cpm)
    df = wv.detect_nonwear(df)
    df['valid'] = np.where(((df['spurious'] == 0) & (df['nonwear'] == 0) & (df['malfunction'] == 0)), 1, 0)
    df['wear'] = np.where(df['nonwear'] == 0, 1, 0)
    
    # Organize dataset and append
    df = df.drop(columns = ['spurious', 'nonwear', 'malfunction'])
    for i in list(df):
        if i not in ['month', 'id', 'date', 'day_of_the_week', 'time', 'time_of_the_day', 'study_day', 'season', 'age']:
            df[i] = np.where(df['valid'] == 0, np.NaN, df[i])
    accel_data = accel_data.append(df, ignore_index = True)
    accel_data = accel_data.sort_values(["month", "id", "date", "time"])

# ------------------------------------------------------------------------------------------------------------------------------------------------------

# Print the cut-points used   
if child_cp != "":
    print("Child cutpoints: {}; {}-axis".format(child_cp, axis))
    for i in cur_set_child:
        print("{} years: {}".format(i, cur_set_child[i]))        
if adult_cp != "":
    print("Adult cutpoints: {}; {}-axis".format(adult_cp, axis))
    for i in cur_set_adult:
        print("{}: {} to {}".format(i, cur_set_adult[i][0], cur_set_adult[i][1]))

        
# Order the variables
group = ['month', 'id', 'date', 'day_of_the_week', 'time', 'time_of_the_day', 'study_day', 'season', 'age']
wear_min = ['valid', 'wear'] 
counts = ['axis1', 'vector_magnitude']
intensities = [x for x in accel_data if x in ['sedentary', 'light', 'moderate', 'vigorous', 'very vigorous', 'mvpa']]
myorder = ["sedentary", "light", "moderate", "vigorous", "very vigorous", "mvpa"]
intensities = [x for x in myorder if x in intensities]
bouts = ['mvpa_bout_counts', 'mvpa_bout_length']
accel_data = accel_data[group + wear_min + counts + intensities + bouts]


# Change to the original data directory and set prefix for the file names to be exported
os.chdir(datadir)
if (child_cp != "") & (adult_cp != ""):    
    name = study + "_" + child_cp + "_" + adult_cp + "_" + str(axis) + "axis"
elif child_cp != "":
    name = study + "_" + child_cp + "_" + str(axis) + "axis"
elif adult_cp != "":
    name = study + "_" + adult_cp + "_" + str(axis) + "axis"

    
# Group the data together by month, id, and date, and time of the day.
g = accel_data.groupby(['month', 'id', 'date', 'day_of_the_week', 'study_day', 'season', 'time_of_the_day', 'age'], as_index = False)   
accel_by_person_datetime = g.agg('sum')
accel_by_person_datetime.sort_values(['month', 'id', 'date', 'day_of_the_week', 'study_day', 'season', 'time_of_the_day', 'age'])
accel_by_person_datetime['time_of_the_day'] = accel_by_person_datetime['time_of_the_day'].str[3:]
accel_by_person_datetime.to_csv(name.lower() + "_" + "by_person_datetime.csv", index=False)


# Group the data together by month, id, and date and add valid days
g = accel_data.groupby(['month', 'id', 'date', 'day_of_the_week', 'study_day', 'season', 'age'], as_index = False)   
accel_by_person_date = g.agg('sum')
accel_by_person_date['valid_day'] = np.where(accel_by_person_date['wear'] >= valid, 1, 0)
accel_by_person_date.to_csv(name.lower() + "_" + "by_person_date.csv", index=False)


# Exclude days that are not valid.
group = ['month', 'id', 'date', 'day_of_the_week', 'study_day', 'season', 'age', 'valid_day']
cols = [x for x in accel_by_person_date if x not in group]
for i in list(accel_by_person_date):    
    if i not in ['month', 'id', 'date', 'day_of_the_week', 'study_day', 'season', 'age']:
        accel_by_person_date[i] = np.where(accel_by_person_date['valid_day'] == 0, np.NaN, accel_by_person_date[i])   
accel_by_person_date_valid_days = accel_by_person_date[~accel_by_person_date['axis1'].isnull()]


# Group the dataset together by month and id and round observations to 2 decimals.
g = accel_by_person_date_valid_days.groupby(['month', 'id'], as_index = False)
accel_by_person = pd.merge(g[cols].mean(), g['valid_day'].sum())
for i in list(accel_by_person):
    if i not in ['month', 'id', 'age']:
        accel_by_person[i] = round(accel_by_person[i], 2)
accel_by_person = accel_by_person.sort_values(['id', 'month']).reset_index(drop=True)
accel_by_person.to_csv(name.lower() + "_" + "by_person.csv", index=False)


# Finish the accelerometer program
print("Accelerometer program completed in %s seconds." % (round((time.time() - start_time), 2))) # Report time to run program
print("Check '%s' for the accelerometer summary." % datadir)


# In[ ]:




