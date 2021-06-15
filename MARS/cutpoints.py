#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np

def cut_points(df, set_name, n_axis):
    """
    Categorize physical activity (PA) counts into intensity categories by age.
    X is the column name of the DataFrame with either vertical counts (Axis #1) or Vector Magnitude.
    New cut-points can be added to these sets.
    """
    sets = {
        "freedson_child": {
            1: {
                5: {"sedentary":[-np.inf, 101],"light":[101, 1291],"moderate":[1291, 3581],"vigorous":[3581, np.inf]},
                6: {"sedentary":[-np.inf, 101],"light":[101, 1400],"moderate":[1400, 3758],"vigorous":[3758, np.inf]},
                7: {"sedentary":[-np.inf, 101],"light":[101, 1515],"moderate":[1515, 3947],"vigorous":[3947, np.inf]},
                8: {"sedentary":[-np.inf, 101],"light":[101, 1638],"moderate":[1638, 4147],"vigorous":[4147, np.inf]},
                9: {"sedentary":[-np.inf, 101],"light":[101, 1770],"moderate":[1770, 4360],"vigorous":[4360, np.inf]},
                10: {"sedentary":[-np.inf, 101],"light":[101, 1910],"moderate":[1910, 4588],"vigorous":[4588, np.inf]},
                11: {"sedentary":[-np.inf, 101],"light":[101, 2059],"moderate":[2059, 4830],"vigorous":[4830, np.inf]},
                12: {"sedentary":[-np.inf, 101],"light":[101, 2220],"moderate":[2220, 5094],"vigorous":[5094, np.inf]},
                13: {"sedentary":[-np.inf, 101],"light":[101, 2393],"moderate":[2393, 5357],"vigorous":[5357, np.inf]},
                14: {"sedentary":[-np.inf, 101],"light":[101, 2580],"moderate":[2580, 5679],"vigorous":[5679, np.inf]},
                15: {"sedentary":[-np.inf, 101],"light":[101, 2781],"moderate":[2781, 6007],"vigorous":[6007, np.inf]},
                16: {"sedentary":[-np.inf, 101],"light":[101, 3000],"moderate":[3000, 6363],"vigorous":[6363, np.inf]},
                17: {"sedentary":[-np.inf, 101],"light":[101, 3239],"moderate":[3239, 6751],"vigorous":[6751, np.inf]},
            }
        },
        "troiano_adult": {
            1: {
                "sedentary":[-np.inf, 101],
                "light":[101, 2020],
                "moderate":[2020, 5999],
                "vigorous":[5999, np.inf],
            }
        },
        "fariasbarnett_adult": {
            1: {
                "sedentary": [-np.inf, 25], # Farias cut-point for sedentary vertical axis
                "light": [25, 1013],
                "mvpa": [1013, np.inf],
            },
            
            3: {
                "sedentary": [-np.inf, 200], # Farias cut-point for sedentary vector magnitude
                "light": [200, 1924],
                "mvpa": [1924, np.inf],
            },
        },
        
        "freedson_adult": {
            1: {
                "sedentary": [-np.inf, 100],
                "light": [100, 1952],
                "moderate": [1952, 5725],
                "vigorous": [5725, 9499],
                "very vigorous": [9499, np.inf],
            },
            3: {
                "sedentary": [-np.inf, 200], # Farias cut-point for sedentary vector magnitude
                "light": [200, 2690],
                "moderate": [2690, 6167],
                "vigorous": [6167, 9642],
                "very vigorous": [9642, np.inf],
            },
        },
    } 
    
    try:
        cur_set = sets[set_name][n_axis]
        
    except KeyError:
        print(
            "Error: cut-point set not found. Make sure the set name and/or "
            "number of axes are correct"
        )
        raise
        
    # categorize counts 
    category = []
    if n_axis==1:
        for i, row in enumerate(df.itertuples()):
            if df.loc[i, 'age'] < 18:
                age = int(df.loc[i, 'age'])
                for intensity in cur_set[age]:
                    if cur_set[age][intensity][0] <= df.loc[i, 'axis1'] < cur_set[age][intensity][1]:
                        category.append(intensity)
                        break

            elif df.loc[i, 'age'] >= 18:
                for intensity in cur_set:
                    if cur_set[intensity][0] <= df.loc[i, 'axis1'] < cur_set[intensity][1]:
                        category.append(intensity)
                        break
            
    elif n_axis==3:
        for i, row in enumerate(df.itertuples()):
            if df.loc[i, 'age'] < 18:
                age = int(df.loc[i, 'age'])
                for intensity in cur_set[age]:
                    if cur_set[age][intensity][0] <= df.loc[i, 'vector_magnitude'] < cur_set[age][intensity][1]:
                        category.append(intensity)
                        break
        
            elif df.loc[i, 'age'] >= 18:
                for intensity in cur_set:
                    if cur_set[intensity][0] <= df.loc[i, 'vector_magnitude'] < cur_set[intensity][1]:
                        category.append(intensity)
                        break

    # Assign intensity cateogry to dataset
    df['intensity'] = category
    df = pd.concat([df, pd.get_dummies(df['intensity'])], axis=1)
    
    mvpa = []

    if "moderate" in category:
        mvpa.append("moderate")
    if "vigorous" in category:
        mvpa.append("vigorous")
    if "very vigorous" in category:
        mvpa.append("very vigorous")

    if 'mvpa' not in category:
        if len(mvpa)==1:
            df['mvpa'] = np.where(df[mvpa[0]]==1, 1, 0)
        elif len(mvpa)==2:
            df['mvpa'] = np.where((df[mvpa[0]]==1) | (df[mvpa[1]]==1), 1, 0)
        elif len(mvpa)==3:
            df['mvpa'] = np.where((df[mvpa[0]]==1) | (df[mvpa[1]]==1) | (df[mvpa[2]]==1), 1, 0)
        else:
            df['moderate'] = 0
            df['vigorous'] = 0
            df['mvpa'] = 0
    
    return df, cur_set


def detect_bouts(data, bout, tol):
    
    data['mvpa_interrupts'] = data.groupby(data.mvpa.eq(1).cumsum()).cumcount().astype(int)

    data['mvpa_bout_length'] = np.where(data.mvpa_interrupts.shift(-(tol+1)).eq((tol+1)), 1, 0)

    for i in range(tol+1):

        data['mvpa_interrupts'] = np.where(data.mvpa_bout_length.shift(i).eq(1), 0, data['mvpa_interrupts'])

    data['mvpa_interrupts'] = np.where((data['mvpa_interrupts']>tol), 0, data['mvpa_interrupts'])

    data['mvpa_interrupts'] = np.where(data.mvpa_interrupts.ne(0), 1, 0)

    data['mvpa_bout_length'] = data['mvpa'] + data['mvpa_interrupts']

    data['mvpa_bout_length'] = data.groupby(data.mvpa_bout_length.eq(0).cumsum()).cumcount().astype(int)

    data['mvpa_bout_length'] = np.where(data['mvpa_bout_length'].shift(-1).eq(0) & data['mvpa_bout_length'].ne(0), data['mvpa_bout_length'], 0)

    data['mvpa_bout_length'] = np.where(data.mvpa_bout_length.ge(bout), data['mvpa_bout_length'], 0)

    data['mvpa_bout_counts'] = np.where(data.mvpa_bout_length.ne(0), 1, 0)

    data = data.drop(columns = ['mvpa_interrupts'])
    
    return data

