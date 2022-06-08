import pandas as pd
import os
import glob
from datetime import datetime as dt
from datetime import timedelta as td
import numpy as np
import ast
from scipy.signal import filtfilt
from scipy.signal import butter

def Exceltocsv(path, name, headers, sheet_name=0, header=0, rows=None, startrow=None, colums=None,):
    """read an Excel file and transform the useful data in a csv
    
    path: str of the path of the file
    name: name of the csv file
    headers: list of the names of the colums in the dataframe (must have the same number of colums entered)
    sheet_name: str or int of the Excel sheet we want to use (the first by default)
    header: last row of the heading where there's not data but for example the name of the colums (0 by default)
    rows: int of the number of the rows we want to store (all by default)
    colums: str of the letter of the solums we want to store (all by default) -- EX: 'A,K' (colums A and K) 
                                                                                     'A-K' (colums A to K)

    return the dataframe and save a csv
    """
    data = pd.read_excel(path, header=header, names=headers, sheet_name=sheet_name, usecols=colums, skiprows = startrow, nrows=rows, na_values='na')
    data = data.dropna()
    data.to_csv(f"{name}.csv", index=False)
    return data

def joincsvfiles(path, common, newname):
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
    dataFrame = pd.concat(map(pd.read_csv, list_files))
    # save the dataframe in a csv
    dataFrame.to_csv(f"{newname}.csv", index=False)
    return dataFrame

def renamefiles_asDanwishes(path):
    """rename all the file of a certain folder with the format "yyyymmdd-*". If a file with its 'new name'
    got the same name of another file (for example an older version), an exception will stop the programm
    and you must delete one of the version to continue (no duplicate will be created!)

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

def add_id(path, name_id, id):
    """add a colum of the same id to all the data of the file chosen
    
    path: str of the path of the file
    name_id: name of the colum we add
    id: str or value of the id
    
    return the dataframe and update the csv
    """
    df = pd.read_csv(path, header=0)
    rows = df.shape[0]
    df[name_id] = [id for _ in range(rows)]
    df.to_csv(path, index=False)
    return df

def stripcolums(path, colums):
    """delete colums of the file chosen
    
    path: str of the path of the file
    colums: list of the name of the colums we want to delete

    return the dataframe and update the csv
    """
    df = pd.read_csv(path, header=0)
    for col in colums:
        df.pop(col)
    df.to_csv(path, index=False)
    return df

def find_date(path, date, newname, headers, cols=None):
    """take only the data from a specific date
    
    path: str of the path of the file
    date: str of the part of time we want to regroup (ex: '2021-01', all of the data in january)
    newname: name of the file with the data filtred
    headers: name of the colums of the new file
    cols: list of the colums' index we want to conserve, all by default

    return the dataframe and save csv
    """
    df = pd.read_csv(path, header=0)
    rows_to_keep = []
    for i, datehour in enumerate(df['date']):
        if date in datehour:
            rows_to_keep.append(i+1)
    data = pd.read_csv(path, header=None, usecols=cols, skiprows= lambda x: x not in rows_to_keep)
    data.to_csv(f"{newname}.csv", index=False, header=headers)
    return data

def norm_file(path, colum):
    """normalize irradiance data according to the max value of the data
    
    path: str of the path of the file
    colum: str of the colum we want to normalize with itself

    return the datafram and update the csv
    """
    df = pd.read_csv(path)
    ira = df[colum]
    max_ira = max(ira)
    norm_ira = []
    for value in ira:
        norm_ira.append(value/max_ira)
    df[f'{colum} self-norm'] = norm_ira
    df.to_csv(path, index=False)
    return df

def norm_irradiance(path, pathref, colums, newname):
    """normalize irradiance data according to a certain reference (i0) who have the same timestamp
    
    path: str of the path of the file in question
    pathref: str of the path of the file who is the reference
    colums: list of the colums we want to use to normalize (first is a str for the file tested and second is a int for the ref)
    newname: str of the name of the dataframe normalized

    return the efficienty of the normalization (number of values greater than 2 and the maximum value) and save csv
    """
    # find corresponding reference
    bigref = pd.read_csv(pathref)
    colref = bigref.columns.values.tolist()
    file = pd.read_csv(path)
    dates = file.date.tolist()
    n = 1
    if colref[colums[1]] != colums[0]:
        raise ValueError('colums are not the same')
    try:
        ref = bigref.loc[bigref['date'] == dates]
        ref = ref[colref[colums[1]]]
        print(49)
    except Exception as err:
        rows_to_keep = []
        for i, datehour in enumerate(bigref['date']):
            if (i+1) >= bigref.shape[0]*n/5:
                print((i+1)/bigref.shape[0]*50)
                n +=1
            if datehour in dates:
                rows_to_keep.append(i+1)
        ref = pd.read_csv(pathref, header=None, skiprows= lambda x: x not in rows_to_keep)[colums[1]]
    ira = pd.read_csv(path)[colums[0]]
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
    file[f'{colums[0]} i0-norm'] = norm_ira
    file.to_csv(f"{newname}.csv", index=False)
    return (len(eff_ref), max(eff_ref), min(eff_ref))

def norm_CRN4(path, pathref, newname):
    """normalize irradiance data according to a certain reference (i0) who don't have the same timestamp 
    
    path: str of the path of the file in question
    pathref: str of the path of the file who is the reference
    newname: str of the name of the dataframe returned

    return dataframe and save csv
    """
    crn4 = pd.read_csv(pathref, header=0)
    cap = pd.read_csv(path, header=0)
    j=0
    rowscrn = crn4.shape[0]
    rowscap = cap.shape[0]
    dicto = {}
    for date in crn4['date']:
        dicto[date] = []
    for i in range(rowscap):
        s1 = cap['date'][i]
        date1 = dt.strptime(s1, '%Y-%m-%d %H:%M:%S')
        print(i/rowscap*100)
        while True:
            if j >= rowscrn:
                break
            s2 = crn4['date'][j]
            date2 = dt.strptime(s2, '%Y-%m-%d %H:%M:%S')
            delta = (date2 - date1).total_seconds()
            if delta < -300:
                j += 1
            elif delta <= 300 and delta >= -300:
                dicto[s2].append(cap['irradiance self-normalized'][i])
                break
            else:
                break
        if j > rowscrn:
            break
    df = pd.DataFrame({'date': dicto.keys(), 'ref':crn4['iswr self-normalized'], 'list': dicto.values()})
    df.to_csv(f"{newname}.csv", index=False)
    return df

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

def stats(path, colum):
    """ calculate the mean and the median of each list in a dataframe of lists
    
    path: str of the path of the file
    colum: str of the name of the colum of the lists
    """
    data = pd.read_csv(path, header=0)
    moy = []
    med = []
    eff_refy = []
    eff_refd = []
    for i, str in enumerate(data[colum]):
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

def denoise(path, colum, filter=0.1):
    """ denoise by a filter a colum of a certain csv file
    
    path: str of the path of the file
    colum: str of the name of the colum we want to denoise
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
    y = data[colum]
    b, a = butter(3, filter)
    w = filtfilt(b, a, y)
    data[f"{colum}_denoised"] = w
    data = data[data['date'] != 'test']
    data.to_csv('path.csv', index=None)
    return data

def norm_std(path, colum, columref):
    """normalize irradiance data according to the max value of the data of another colum
    because the colum is too noised
    
    path: str of the path of the file
    colum: str of the colum we want to normalize
    columref: colum who has the maximum at the index we want

    return the datafram and update the csv
    """
    df = pd.read_csv(path)
    ira = df[colum]
    ref = df[columref]
    indexref = df.loc[df[columref] == max(ref)].index[0]
    max_ira = ira.loc[indexref]
    norm_ira = []
    eff = []
    for value in ira:
        norm_ira.append(value/max_ira)
        if value/max_ira > 2 or value/max_ira < -1:
            eff.append(value/max_ira)
    df[f'{colum} std-norm'] = norm_ira
    df.to_csv(path, index=False)
    return (len(eff), max(eff), min(eff))

def check_eff(path):
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
            print("{} {}: {}".format(i, col, len(eff)))
    pass
#enter your path here
path1 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\'
path2 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\400F650_norm.csv'
newname = 'test'
headers = ['date', 'irradiance']
colum = ["irradiance self-norm", 2]
# print(denoise(path2, 10, 'irradiance self-normalized'))
cols = [('1000', 'J'), ('1200', 'L'), ('1375', 'N')] #('485', 'D'), ('650', 'F'), 
for c, i in cols:
    print(check_eff(f'{path1}400F650_norm{c}.csv'))
