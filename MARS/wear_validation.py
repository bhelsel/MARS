#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np

def detect_malfunction(y):
    y.loc[0, 'nochange'] = 0
    y['nochange'] = np.where((y['axis1'].eq(y['axis1'].shift(1))) & (y['axis1'] != 0), 1, 0)
    y['spurious'] = np.where(y['axis1'] >= 20000, 1, 0)
    y['nochange_counts'] = y.groupby(y.nochange.eq(0).cumsum()).cumcount().shift(-1).fillna(method='pad').astype(int)
    y['malfunction'] = np.where(y['nochange_counts'] >= 10, 1, 0)
    y['malf_marker'] = np.where(y['nochange_counts'] == 10, 1, 0)
    nochange_list = list(range(1, 10))
    for i, row in enumerate(y.itertuples()):
        if y.loc[i, 'malf_marker'] == 1:
            for nc in nochange_list:
                y.loc[i-nc, 'malfunction'] = 1
    y = y.drop(columns = ['malf_marker', 'nochange', 'nochange_counts'])
    return y

def detect_nonwear(y):
    y.loc[0, 'nonwear'] = 0
    y.loc[0, 'naughts'] = 0
    y['naughts'] = np.where(y['axis1'] == 0, 1, 0)
    y['naught_counts'] = y.groupby(y.naughts.eq(0).cumsum()).cumcount().shift(-1).fillna(method='pad').astype(int)
    y['nonwear'] = np.where(y['naught_counts'] >= 60, 1, 0)
    y['nonw_marker'] = np.where(y['naught_counts'] == 60, 1, 0)
    nonwear_list = list(range(1, 60))
    for i, row in enumerate(y.itertuples()):
        if y.loc[i, 'nonw_marker'] == 1:
            for nw in nonwear_list:
                y.loc[i-nw, 'nonwear'] = 1
    y = y.drop(columns = ['naughts', 'naught_counts', 'nonw_marker'])
    return y

