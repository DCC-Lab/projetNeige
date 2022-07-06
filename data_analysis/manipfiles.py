from operator import index
from unittest import result
import pandas as pd
import os
import glob
from datetime import datetime as dt
from datetime import timedelta as td
import numpy as np
import ast
import scipy.signal as ss

# Read fonctions
def Exceltocsv(path, name, headers, sheet_name=0, header=0, rows=None, startrow=None, columns=None):
    """read an Excel file and transform the useful data in a csv
    
    path: str of the path of the file
    name: name of the csv file
    headers: list of the names of the columns in the dataframe (must have the same number of columns entered)
    sheet_name: str or int of the Excel sheet we want to use (the first by default)
    header: last row of the heading where there's not data but for example the name of the columns (0 by default)
    rows: int of the number of the rows we want to store (all by default)
    startrow: int/list of the row/s we want to skip (None by default)
    columns: str of the letter of the solums we want to store (all by default) -- EX: 'A,K' (columns A and K) 
                                                                                     'A-K' (columns A to K)

    return the dataframe and save a csv
    """
    data = pd.read_excel(path, header=header, names=headers, sheet_name=sheet_name, usecols=columns, skiprows = startrow, nrows=rows, na_values='na')
    # data = data.dropna()
    data.to_csv(f"{name}.csv", index=False)
    return data

# Modify many files
def joincsvfilescom(path, common, newname):
    """join csv files with a similar name in alphabetic order
    
    path: str of the common path of the files
    common: str of what is similar in all the files you want to join
    newname: name of the new file

    return the dataframe and save a csv
    """
    # takes the files and put them in a list
    files_joined = os.path.join(path, f"*{common}*.csv")
    list_files = glob.glob(files_joined)
    # join the files in a dataframe panda
    dataframe = pd.concat(map(pd.read_csv, list_files))
    # save the dataframe in a csv
    dataframe.to_csv(f"{newname}.csv", index=False)
    return dataframe

def joincsvfilesname(path, names, newname):
    """join csv files entered in alphabetic order
    
    path: str of the common path of the files
    names: list of the names (str) of all the files you want to join
    newname: name of the new file

    return the dataframe and save a csv
    """
    files = os.listdir(path)
    for name in files:
        if name in names:
            nfc = os.path.join(path, name)
            os.rename(nfc, os.path.join(path, "qqq-" + name))
    dataframe = joincsvfilescom(path, 'qqq-', newname)
    strip_names(path)
    return dataframe

def strip_names(path, error='qqq-'):
    """delete a string of the name of the files of a certain folder
    
    path: str of the common path of the files
    error: str of the charaters we want to delete (will delete only the first encountered)

    return a confirmation that it's done
    """
    files = os.listdir(path)
    i = 1
    for name in files:
        if error in name:
            print(f'find {i}')
            nfc = os.path.join(path, name)
            os.rename(nfc, os.path.join(path, name.replace(error, '', 1)))
            i += 1
    return "it's done!"

def renamefiles_asDanwishes(path):
    """rename all the file of a certain folder with the format "yyyymmdd-*". If a file with its 'new name'
    got the same name of another file (for example an older version), an exception will stop the programm
    and you must delete/rename one of the version to continue (no duplicate will be created!)

    path: str of the path to the folder
    
    nothing is return but a confirmation is printed to say that it has been done
    """
    names = os.listdir(path)
    # Here I assume that the new files put in the folder were created/updated today, you can change it as you wish
    date = dt.today().strftime("%Y%m%d")
    for name in names:
        nfc = os.path.join(path, name)
        # I know that I have only files of this year in my folder and no "ID" contains "2022" in the name, except those who are already renamed
        # you must add other exceptions for other years if that is the case
        if "2022" not in name:
            os.rename(nfc, os.path.join(path, f"{date}-" + name))
    print("It's done!")
    return "Yeah :)"

# Modify one file/dataframe
def add_id(path, name_id, id):
    """add a column of the same id to all the data of the file chosen
    
    path: str of the path of the file
    name_id: name of the column we add
    id: str or value of the id
    
    return the dataframe and update the csv
    """
    df = pd.read_csv(path, header=0)
    rows = df.shape[0]
    df[name_id] = [id for _ in range(rows)]
    df.to_csv(path, index=False)
    return df

def stripcolums(path, columns):
    """delete columns of the file chosen
    
    path: str of the path of the file
    columns: list of the name of the columns we want to delete

    return the dataframe and update the csv
    """
    df = pd.read_csv(path, header=0)
    for col in columns:
        try:
            df.pop(col)
        except KeyError:
            pass
    df.to_csv(path, index=False)
    return df

def find_dates(path, dates, newname, headers, cols=None):
    """take only the data from a or many specific date/s
    
    path: str of the path of the file
    dates: list of str of the part of time we want to regroup (ex: '2021-01', all of the data in january)
    newname: name of the file with the data filtred
    headers: name of the columns of the new file
    cols: list of the columns' index we want to conserve, all by default

    return the dataframe and save csv
    """
    df = pd.read_csv(path, header=0)
    rows_to_keep = []
    for date in dates:
        for i, datehour in enumerate(df['date']):
            if date in datehour:
                rows_to_keep.append(i+1)
    data = pd.read_csv(path, header=None, usecols=cols, skiprows= lambda x: x not in rows_to_keep)
    data.to_csv(f"{newname}.csv", index=False, header=headers)
    return data

# Normalization fonctions
def norm_file(path, column):
    """normalize irradiance data according to the max value of the data
    
    path: str of the path of the file
    column: str of the column we want to normalize with itself

    return the dataframe and update the csv
    """
    df = pd.read_csv(path)
    ira = df[column]
    max_ira = max(ira)
    norm_ira = []
    for value in ira:
        norm_ira.append(value/max_ira)
    df[f'{column} self-norm'] = norm_ira
    df.to_csv(path, index=False)
    return df

def norm_calibrate(path, column, date='2020-12-12 10:25:15'):
    """normalize irradiance data according to a certain value of the data
    
    path: str of the path of the file
    column: str of the column we want to normalize with itself
    date: str of the date the certain value is ('2020-12-12 10:25:15' by default)

    return the dataframe and update the csv
    """
    df = pd.read_csv(path)
    ira = df[column]
    indexref = df.loc[df['date'] == date].index[0]
    ref_ira = np.mean(ira.loc[indexref-1:indexref+1])
    norm_ira = []
    for value in ira:
        norm_ira.append(value/(ref_ira*83))
    df[f'{column} self-norm'] = norm_ira
    df.to_csv(path, index=False)
    return df

def norm_irradiance(path, pathref, columns, newname):
    """normalize irradiance data according to a certain reference (i0) who have the same timestamp
    
    path: str of the path of the file in question
    pathref: str of the path of the file who is the reference
    columns: list of the columns we want to use to normalize (first is a str for the file tested and second is a int for the ref)
    newname: str of the name of the dataframe normalized

    return the efficienty of the normalization (number of values greater than 2 and the maximum value) and save csv
    """
    # find corresponding reference
    bigref = pd.read_csv(pathref)
    colref = bigref.columns.values.tolist()
    file = pd.read_csv(path)
    dates = file.date.tolist()
    n = 1
    if colref[columns[1]] != columns[0]:
        raise ValueError('columns are not the same')
    try:
        ref = bigref.loc[bigref['date'] == dates]
        ref = ref[colref[columns[1]]]
        print(49)
    except Exception as err:
        rows_to_keep = []
        for i, datehour in enumerate(bigref['date']):
            if (i+1) >= bigref.shape[0]*n/5:
                print((i+1)/bigref.shape[0]*50)
                n +=1
            if datehour in dates:
                rows_to_keep.append(i+1)
        ref = pd.read_csv(pathref, header=None, skiprows= lambda x: x not in rows_to_keep)[columns[1]]
    ira = pd.read_csv(path)[columns[0]]
    norm_ira = []
    eff_ref = []
    n = 1
    # calculate the normalized irradiance
    for i in range(ira.shape[0]):
        if (i+1) >= ira.shape[0]*n/5:
            print(50+(i+1)/ira.shape[0]*50)
            n += 1
        if ref[i] == 0:
            norm_ira.append(0)
        else:
            norm_ira.append(ira[i]/ref[i])
            if ira[i]/ref[i] > 2 or ira[i]/ref[i] < -1:
                eff_ref.append(ira[i]/ref[i])
    # store the result
    file[f'{columns[0]} i0-norm'] = norm_ira
    file.to_csv(f"{newname}.csv", index=False)
    return (len(eff_ref), max(eff_ref), min(eff_ref))

def norm_CRN4(path, pathref, columns, newname, window=5, order=0, how=['mean', 'median']):
    """normalize irradiance data according to a certain reference (i0) who don't have the same timestamp 
    
    path: str of the path of the file in question
    pathref: str of the path of the file who is the reference
    columns: list of the name of the columns we want (first the one we want to normalize, second the reference)
    newname: str of the name of the dataframe returned
    window: int of the number of minutes that we use for the mean/median (5 by default)
    order: int between 0 and 1 -- 1 represent the (rolling) mean/median at the right and 0 at the center (0 by default)
    how: list of the name of the method(s) used for the (rolling) ""mean/median"" (both by default)

    return dataframe and save csv
    """
    if (how not in ['mean', 'median'] and how != ['mean', 'median']) or (order not in [0, 1]):
        raise NotImplemented
    reference = pd.read_csv(pathref, header=0)
    study = pd.read_csv(path, header=0)
    j, n = 0, 0
    rowsref = reference.shape[0]
    rowsstu = study.shape[0]
    dicto = {}
    for date in reference['date']:
        dicto[date] = []
    for i in range(rowsstu):
        s1 = study['date'][i]
        date1 = dt.strptime(s1, '%Y-%m-%d %H:%M:%S')
        if (i+1) >= rowsstu*n/10:
                print((i+1)/rowsstu*100)
                n +=1
        while True:
            if j >= rowsref:
                break
            s2 = reference['date'][j]
            date2 = dt.strptime(s2, '%Y-%m-%d %H:%M:%S')
            delta = (date2 - date1).total_seconds()
            if order == 0:
                if delta < -window*60:
                    j += 1
                elif delta <= window*60 and delta >= -window*60:
                    dicto[s2].append(study[columns[0]][i])
                    break
                else:
                    break
            else:
                if delta < 0:
                    j += 1
                elif delta <= window*60 and delta >= 0:
                    dicto[s2].append(study[columns[0]][i])
                    break
                else:
                    break
        if j > rowsref:
            break
    data = pd.DataFrame({'date': dicto.keys(), 'ref':reference[columns[1]], 'list': dicto.values()})
    for method in how:
        values = []
        eff = []
        for i, liste in enumerate(data['list']):
            if liste != [] and data['ref'][i] != 0:
                if method == 'mean':
                    value = np.mean(liste/data['ref'][i])
                else:
                    value = np.median(liste/data['ref'][i])
                values.append(value)
                if value > 2  or value < -1:
                    eff.append(value)
            else:
                values.append(np.nan)
        data[f'{method}_norm'] = values
        if len(eff) == 0:
            print(len(eff), max(values), min(values))
        else:
            print(len(eff), max(eff), min(eff))
    data.pop('ref')
    data.pop('list')
    data.to_csv(f'{newname}.csv', index=None)
    return data

def norm_std(path, column, columref):
    """normalize irradiance data according to the max value of the data of another column
    because the column is too noised
    
    path: str of the path of the file
    column: str of the column we want to normalize
    columref: column who has the maximum at the index we want

    return the dataframe and update the csv
    """
    df = pd.read_csv(path)
    ira = df[column]
    ref = df[columref]
    indexref = df.loc[df[columref] == max(ref)].index[0]
    max_ira = ira.loc[indexref]
    norm_ira = []
    eff = []
    for value in ira:
        norm_ira.append(value/max_ira)
        if value/max_ira > 2 or value/max_ira < -1:
            eff.append(value/max_ira)
    df[f'{column} std-norm'] = norm_ira
    df.to_csv(path, index=False)
    if len(eff) == 0:
        a, b, c = len(eff), max(norm_ira), min(norm_ira)
    else:
        a, b, c = len(eff), max(eff), min(eff)
    return (a, b, c)

# Denoise fonctions
def denoise_but(path, column, filter=0.1):
    """ denoise by a filter a column of a certain csv file
    
    path: str of the path of the file
    column: str of the name of the column we want to denoise
    filter: float of the number of "precision" we want (0.1 by default)

    return dataframe and update the csv
    """
    data = pd.read_csv(path)
    date1 = data['date'][0]
    for i, date2 in enumerate(data['date'][1:]):
        if date1[:10] != date2[:10]:
            a = pd.DataFrame(data.iloc[i+1])
            a.iat[0, 0] = 'test'
            a = pd.DataFrame.transpose(a)
            for n in range(1, 10):
                data.loc[i+n/10] = a.values.tolist()[0]
        date1 = date2
    data = data.sort_index().reset_index(drop=True)
    y = data[column]
    b, a = ss.butter(3, filter)
    w = ss.filtfilt(b, a, y)
    data[f"{column}_denoised"] = w
    data = data[data['date'] != 'test']
    data.to_csv(path, index=None)
    return data

def denoise_mea(path, column, order=1, window=7):
    """ denoise by a moving average a column of a certain csv file
    
    path: str of the path of the file
    column: str of the name of the column we want to denoise
    order: 1 or -1, way of the moving average (left to right or the opposite)
    window: int of the number of minutes we use for the mean (7 minutes by default)

    return dataframe and update the csv
    """
    dic = {1: 'L', -1: 'R'}
    data = pd.read_csv(path)
    y = data[column].to_list()
    dates = []
    for date in data['date']:
        dates.append(dt.strptime(date, '%Y-%m-%d %H:%M:%S'))
    df = pd.DataFrame({'date': dates[::order], f'{column}': y[::order]})
    w = df.rolling(f'{window}T', on='date').mean()
    data[f"{column}_denoised{dic[order]}"] = w.iloc[:, 1].to_list()[::order]
    data.to_csv(path, index=False)
    return df

def denoise_exp(path, column, order=1, window=7):
    """ denoise by a moving exponential average a column of a certain csv file
    
    path: str of the path of the file
    column: str of the name of the column we want to denoise
    window: int of the number of minutes we use for the mean (7 minutes by default)

    return dataframe and update the csv
    """
    dic = {1: 'L', -1: 'R'}
    data = pd.read_csv(path)
    y = data[column].to_list()
    dates = []
    for date in data['date']:
        dates.append(dt.strptime(date, '%Y-%m-%d %H:%M:%S'))
    df = pd.DataFrame({'date': dates[::order], f'{column}': y[::order]})
    w = df[f'{column}'].ewm(halflife=td(minutes=window*order), times=df['date'], ignore_na=True).mean()
    w = w.to_list()
    data[f"{column}_denoised{dic[order]}"] = w[::order]
    data.to_csv(path, index=False)
    return data

def denoise_med(path, column, order=-1, window=15):
    """ denoise by a moving median a column of a certain csv file
    
    path: str of the path of the file
    column: str of the name of the column we want to denoise
    order: 1 or -1, way of the moving median (right to left or the opposite)
    window: int of the number of minutes we use for the mean (15 minutes by default)

    return dataframe and update the csv
    """
    dic = {1: 'L', -1: 'R'}
    data = pd.read_csv(path)
    y = data[column].to_list()
    dates = []
    for date in data['date']:
        dates.append(dt.strptime(date, '%Y-%m-%d %H:%M:%S'))
    df = pd.DataFrame({'date': dates[::order], f'{column}': y[::order]})
    w = df.rolling(f'{window}T', on='date').median()
    data[f"{column}_denoised{dic[order]}"] = w.iloc[:, 1].to_list()[::order]
    data.to_csv(path, index=False)
    return data

# Various fonctions
def check_eff(path):
    """Run a kind of evaluation of the data and print the max and min value plus the number of data who are out of a certain range
    for each column of the file
    
    path: str of the path of the file

    return nothing
    """
    data = pd.read_csv(path)
    cols = sorted(data.columns[1:])
    for i, col in enumerate(cols):
        eff = []
        for value in data[col]:
            if value > 2 or value < -1:
                eff.append(value)
        if eff != []:
            print("{} {}: {}, {}, {}".format(i, col, len(eff), max(eff), min(eff)))
        else:
            print("{} {}: {}, {}, {}".format(i, col, len(eff), max(data[col]), min(data[col])))
    pass

def same_date(s1, s2, resolution):
    """find the difference between 2 dates and return True if the difference is less than the resolution, no matter the order the dates are entered (if not retrun False)
    s1: str of the first date of format '%Y-%m-%d %H:%M:%S'
    s2: str of the second date of format '%Y-%m-%d %H:%M:%S'
    resolution: time interval in seconds where the dates are assumed to be the same 

    return: a bool of the answer
    """
    date1 = dt.strptime(s1, '%Y-%m-%d %H:%M:%S')
    date2 = dt.strptime(s2, '%Y-%m-%d %H:%M:%S')
    a = (date2 - date1).total_seconds()
    if a <= resolution and a >= -resolution:
        return True
    return False

def stats(path, column):
    """ calculate the mean and the median of each list in a dataframe of lists
    
    path: str of the path of the file
    column: str of the name of the column of the lists
    """
    data = pd.read_csv(path, header=0)
    moy = []
    med = []
    eff_refy = []
    eff_refd = []
    for i, str in enumerate(data[column]):
        liste = ast.literal_eval(str)
        if liste and data['ref'][i] != 0:
            moy.append(np.mean(liste)/data['ref'][i])
            med.append(np.median(liste)/data['ref'][i])
            if np.mean(liste)/data['ref'][i] > 2:
                eff_refy.append(np.mean(liste)/data['ref'][i])
            if np.median(liste)/data['ref'][i] > 2:
                eff_refd.append(np.median(liste)/data['ref'][i])
        else:
            moy.append(np.nan)
            med.append(np.nan)
    data['mean_norm'] = moy
    data['median_norm'] = med
    data.to_csv(path, index=None)
    return (len(eff_refy)/len(moy)*100, max(eff_refy), len(eff_refd)/len(med)*100, max(eff_refd))

# Correct raw data
def dates_problem(path, column):
    """ Find the problematic dates of a csv file. In other words, check if the values of a day start by decreasing.

    path: str of the path of the file
    column: str of the name of the column we want to check

    return the list of the dates corresponding to the actual beginning of the day 
    """
    data = pd.read_csv(path)
    df = pd.DataFrame({f'{column}': data[column].to_list()}, index=data['date'].to_list())
    date1 = df.index[0]
    dates = []
    for i, date2 in enumerate(df.index[1:]):
        if date1[:10] != date2[:10]:
            a = df[column].iloc[i+1:i+4].mean()
            b = df[column].iloc[i+4:i+7].mean()
            if (a > b and a-b > 0.0002) or date2[:10] == '2021-04-07':
                day_am = df.loc[(df.index >= date2) & (df.index < f'{date2[:10]} 12{date2[13:]}')]
                if day_am.empty:
                    continue
                dmin = day_am[column].astype(float).idxmin()
                dates.append(dmin)
        date1 = date2
    print('\n')
    return dates

def organize_data(path, column, newname, dates):
    """ Replace the problematic dates entered to the proper day (the day before)

    path: str of the path of the file
    column: str of the name of the column we want to correct
    newname: str of the name of the file modified
    dates: list of the problematic dates (in str) we need to correct (see the fonction dates_problem)

    return the new dataframe and save it if all the dates were modified only once
    if not raise a ValueError
    """
    data = pd.read_csv(path)
    df = pd.DataFrame({f'{column}': data[column].to_list()}, index=data['date'].to_list())
    date1 = df.index[0]
    n, count, x = 1, 0, len(dates)
    for i, date2 in enumerate(df.index[1:]):
        if date1[:10] != date2[:10]:
            for dmin in dates:
                if date2[:10] == dmin[:10]:
                    wrongdates = df.loc[date2:dmin].iloc[:-1]
                    if wrongdates.empty:
                        continue
                    wrongstart = dt.strptime(date2, '%Y-%m-%d %H:%M:%S')
                    realstart = dt.strptime(date1, '%Y-%m-%d %H:%M:%S')
                    for i, date in enumerate(wrongdates.index):
                        realdate = dt.strftime((dt.strptime(date, '%Y-%m-%d %H:%M:%S')-wrongstart+realstart), '%Y-%m-%d %H:%M:%S')
                        data.loc[data['date'] == date, 'date'] = realdate
                    count += 1
                    dates.remove(dmin)
                    continue
        date1 = date2
        if (i+1) >= df.shape[0]*n/10:
            print((i+1)/df.shape[0]*100)
            n += 1
    if count == x != 0 and len(dates) == 0:
        data.to_csv(f'{newname}.csv', index=False)
        return data
    else:
        raise ValueError("the correction did not work, see the lenght of the variable 'dates'")

# Identify periods
def find_period(path, height, window=[-3, 3]):
    """find differents periods where the height of a file is between the window entered
    
    path: str of the path of the file
    height: float of the height we want to analyse
    window: list of float that reprensent the range of values around the height we want

    return a dataframe of the periods of time (and height assciate) with the type (start, end, only) of the date
    """
    data = pd.read_csv(path).sort_values(by='date', ignore_index=True)
    period = data.loc[data['height'] >= height+window[0]]
    period = period.loc[period['height'] <= height+window[1]]
    a = period.index[0]
    start, end = [a], []
    for b in period.index[1:]:
        if a+1 != b:
            start.append(b)
            end.append(a)
        a = b
    end.append(b)
    only = list(set(start) & set(end))
    print(only)
    first, second, alone = data.iloc[start, :2], data.iloc[end, :2], data.iloc[only, :2]
    first, second = first.drop(index=only), second.drop(index=only)
    first['type'], second['type'], alone['type'] = ['start' for _ in range(len(start)-len(only))], ['end' for _ in range(len(end)-len(only))], ['only' for _ in range(len(only))]
    result = pd.concat([first, second, alone], axis=0).sort_index()
    return result.reset_index(drop=True)

def find_weather(path, weather=71, window=[-2, 6], night=True):
    """find significative periods where the weather of a file is between the window entered
    
    path: str of the path of the file
    weather: float between 0 and 89 of the value of weather we want to analyze
             (50-59: soft rain, 60-69: rain, 70-79: snow, 80-89: hail)
    window: list of float that reprensent the range of values around the weather we want
    night: bool to precise if we want the values during the night or not (Yes/True by default)

    return a dataframe of the periods of time (and weather associate) with the type (start, end) of the date
    """
    data = pd.read_csv(path).sort_values(by='date', ignore_index=True)
    period = data.loc[data['median_norm 900-1'] >= weather+window[0]]
    period = period.loc[period['median_norm 900-1'] <= weather+window[1]]
    if night is False:
        period = period.drop(index=(i for i, date, mea, med in period.itertuples() if date[11:16] > '20:15' or date[11:16] < '06:25'))
    a, c = period.index[0], period.index[0]
    start, end = [], []
    for b in period.index[1:]:
        if a+2 < b:
            if a-c > 2 or a-c == 0:
                start.append(c)
                end.append(a)
            c = b
        a = b
    start.append(c)
    end.append(a)
    only = list(set(start) & set(end))
    first, second = data.iloc[start, [0, 2]], data.iloc[end, [0, 2]]
    first, second = first.drop(index=only), second.drop(index=only)
    first['type'], second['type'] = ['start' for _ in range(len(start)-len(only))], ['end' for _ in range(len(end)-len(only))]
    result = pd.concat([first, second], axis=0).sort_index()
    return result.reset_index(drop=True).to_string()

def whatweather():


    pass

#enter your path here
path1 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\all_heightsT4.csv'
path2 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\weather.csv'
# newname = 
headers = ['date', 'precipitation']
columns = ['precipitation', 'Nothing']
dates = [
    '2020-12-25 09:40:55',
    '2020-12-26 07:01:30',
    '2021-01-27 07:02:23',
    '2021-02-24 07:13:18',
    '2021-03-01 08:07:04',
    '2021-03-04 07:11:16',
    '2021-03-11 07:30:11',
    '2021-03-14 07:55:09',
    '2021-03-15 08:04:01',
    '2021-03-16 07:49:33',
    '2021-03-17 07:46:39',
    '2021-03-18 07:55:57',
    '2021-03-19 07:48:06',
    '2021-03-20 07:58:11',
    '2021-03-21 07:47:56',
    '2021-03-22 07:46:51',
    '2021-03-23 07:44:18',
    '2021-03-24 07:55:42',
    '2021-03-27 08:04:56',
    '2021-03-28 08:46:11',
    '2021-03-30 08:04:28',
    '2021-03-31 09:30:57',
    '2021-04-03 07:46:12',
    '2021-04-04 07:42:38',
    '2021-04-05 07:49:42',
    '2021-04-06 08:36:31',
    '2021-04-07 08:15:32',
    '2021-04-08 08:28:13'
    ]
print(find_weather(path2, 71, [0, 0]))
# print(add_id(path1, 'Nothing', 1))
cols = [('325', 'B'), ('485', 'D'), ('650', 'F'), ('1000', 'J'), ('1200', 'L'), ('1375', 'N')] # 
# for c, i in cols[:3]:
#     for co, il in cols[3:]:

