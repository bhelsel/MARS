#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import pandas as pd
import numpy as np
import sqlite3
import pytz
import shutil
import time
import csv

def read_accel_data(accel_data):
    accel_data['dataTimestamp'] = pd.to_datetime(((accel_data['dataTimestamp'] / 10000000) - 62135596800), unit='s')
    accel_data['Date'] = [d.date() for d in accel_data['dataTimestamp']]
    accel_data['Date'] = pd.to_datetime(accel_data['Date']).dt.strftime("%m/%d/%Y")
    accel_data[' Time'] = [d.time() for d in accel_data['dataTimestamp']]
    
    try:
        accel_data = accel_data.rename(columns={"axis1": " Axis1", "axis2": "Axis2", "axis3": "Axis3",
               "steps": "Steps", "lux": "Lux", "inclineOff": "Inclinometer Off", 
               "inclineStanding": "Inclinometer Standing", "inclineSitting": "Inclinometer Sitting",
               "inclineLying": "Inclinometer Lying"})
        accel_data['Vector Magnitude'] = round(np.sqrt(accel_data[' Axis1']**2 + accel_data['Axis2']**2 + accel_data['Axis3']**2), 2)
      
    
    except:
        accel_data = accel_data.rename(columns={"axis1": " Axis1", "steps": "Steps", "lux": "Lux",
               "inclineOff": "Inclinometer Off", "inclineStanding": "Inclinometer Standing",
               "inclineSitting": "Inclinometer Sitting", "inclineLying": "Inclinometer Lying"})
        accel_data.insert(2, "Axis2", np.nan)
        accel_data.insert(3, "Axis3", np.nan)
        accel_data['Vector Magnitude'] = np.nan

    cols = ['Date', ' Time', ' Axis1', 'Axis2', 'Axis3', 'Steps', 'Lux', 'Inclinometer Off', 'Inclinometer Standing', 
            'Inclinometer Sitting', 'Inclinometer Lying', 'Vector Magnitude']
    accel_data = accel_data.drop(columns=['dataTimestamp'])
    accel_data = accel_data[cols]
    return accel_data

def read_accel_settings(accel_set, output_file='test_output.csv'):
    d = dict([(t.settingName, (t.settingValue)) for t in accel_set.itertuples()])
    start_datetime = str(pd.to_datetime(((int(d["startdatetime"]) / 10000000) - 62135596800), unit='s').strftime("%m/%d/%Y %H:%M:%S"))
    start_date = start_datetime.split(" ")[0]
    start_time = start_datetime.split(" ")[1]
    download_datetime = str(pd.to_datetime(((int(d["downloaddatetime"]) / 10000000) - 62135596800), unit='s').strftime("%m/%d/%Y %H:%M:%S"))
    download_date = download_datetime.split(" ")[0]
    download_time = download_datetime.split(" ")[1]
    epochlength = pd.to_datetime(d["epochlength"], unit='s').strftime("%H:%M:%S")
    r1 = ["------------ Data Table File Created By Actigraph" + " " + d["devicename"] + " " + d["softwarename"] + " v" + d["softwareversion"] + " " + "date format" + " " + d["datetimeformat"] + " " + "Filter" + " " + d["filter"] + " -----------"]
    r2 = ["Serial Number:" + " " + d["deviceserial"]]
    r3 = ["Start Time" + " " + start_time]
    r4 = ["Start Date" + " " + start_date]
    r5 = ["Epoch Length (hh:mm:ss)" + " " + epochlength]
    r6 = ["Download Time" + " " + download_time]
    r7 = ["Download Date" + " " + download_date]
    r8 = ["Current Memory Address:" + " " + "0"]
    r9 = ["Current Battery Voltage:" + " " + d["batteryvoltage"] + "     " + "Mode" + " = " + d["modenumber"]]
    r10 = ["--------------------------------------------------"]
    accel_set = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10]
    return accel_set

def to_csv(data_directory):
    start_time = time.time()
    os.chdir(data_directory)
    new_data_directory = data_directory + '/CSV'
    if os.path.exists(new_data_directory) == False:
        os.mkdir('CSV')
    files = sorted(os.listdir())
    agd_files = [file for file in files if file[-4:].lower()=='.agd']
    count = 0
    for file in agd_files:
        new_filename = file[:-4] + '.csv'
        if os.path.exists(new_data_directory + '/' + new_filename) == True:
            continue
            print('The filename "%s" already exists.' % new_filename)
        else:
            count += 1
            con = sqlite3.connect(file)
            accel_data = pd.read_sql_query("SELECT * from data", con)
            accel_set = pd.read_sql_query("SELECT settingName, settingValue from settings", con)
            accel_data = read_accel_data(accel_data)
            accel_set = read_accel_settings(accel_set)
            print('converting %s' % file)
            with open(new_filename, 'w') as csv_file:
                for value in accel_set: 
                    writer = csv.writer(csv_file)
                    writer.writerow(value)
            csv_file.close
            accel_data.to_csv(new_filename, mode='a', index=False)
            con.close()
            shutil.move(os.path.join(data_directory, new_filename), new_data_directory)
    print("All done! This accelerometer program took %s seconds to convert %s records." % (round((time.time() - start_time), 2), count))
    return new_data_directory

