import pandas as pd
import os
import glob
from datetime import datetime as dt

def Exceltocsv(path, name, headers, sheet_name=0, header=0, rows=None, colums=None,):
    """read an Excel file and transform the useful data in a csv
    
    path: str of the path of the file
    name: name of the csv file
    headers: list of the names of the colums in the dataframe (must have the same number of colums entered)
    sheet_name: str or int of the Excel sheet we want to use (the first by default)
    header: last row of the heading where there's not data but for example the name of the colums (0 by default)
    rows: int of the number of the rows we want to store (all by default)
    colums: str of the letter of the solums we want to store (all by default) -- EX: 'A,K' (colums A and K) 
                                                                                     'A-K' (colums A to K)

    return the data and save a csv
    """
    data = pd.read_excel(path, header=header, names=headers, sheet_name=sheet_name, usecols=colums, nrows=rows, na_values='na')
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
    
    nothing is return but a confirmation is printed to say that it has been donne
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
    print("It's done! Yeah :)")

def add_id(path, name_id, id, newname):
    """add a colum of the same id to all the data of the file chosen
    
    path: str of the path of the file
    name_id: name of the colum we add
    id: str or value of the id
    newname: name of the file modified
    
    return the dataframe and save csv
    """
    df = pd.read_csv(path, header=0)
    rows = df.shape[0]
    df[name_id] = [id for _ in range(rows)]
    df.to_csv(f"{newname}.csv", index=False)
    return df

def stripcolums(path, newname, colums):
    """delete colums of the file chosen
    
    path: str of the path of the file
    newname: name of the file modified
    colums: list of the name of the colums we want to delete

    return the dataframe and save csv
    """
    df = pd.read_csv(path, header=0)
    for col in colums:
        df.pop(col)
    df.to_csv(f"{newname}.csv", index=False)
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

def normalize_file(path):
    """normalize irradiance data according to the max value of the data
    
    path: str of the path of the file

    return the datafram and update the csv file
    """
    df = pd.read_csv(path)
    ira = df.irradiance
    max_ira = max(ira)
    norm_ira = []
    for value in ira:
        norm_ira.append(value/max_ira)
    df['irradiance self-normalized'] = norm_ira
    df.to_csv(path, index=False)
    return df

def normalize_irradiance(path, pathref, newname):
    """normalize irradiance data according to a certain reference (i0)
    
    path: str of the path of the file in question
    pathref: str of the path of the file who is the reference
    newname: name of the file with the irradiance normalized

    return the dataframe and save csv
    """
    # find corresponding reference
    bigref = pd.read_csv(pathref)
    dates = pd.read_csv(path).date.tolist()
    rows_to_keep = []
    for i, datehour in enumerate(bigref['date']):
        if datehour in dates:
            rows_to_keep.append(i+1)
    ref = pd.read_csv(pathref, header=None, skiprows= lambda x: x not in rows_to_keep)[:][2].tolist()
    ira = pd.read_csv(path)['irradiance self-normalized'].tolist()
    norm_ira = []
    eff_ref = []
    # calculate the normalized irradiance
    for i in range(len(ira)):
        if ref[i] == 0:
            norm_ira.append(0)
        else:
            norm_ira.append(ira[i]/ref[i])
            if ira[i]/ref[i] > 2:
                eff_ref.append(ira[i]/ref[i])
    # store the result
    norm_ira = pd.DataFrame({'date': dates, 'irradiance i0-normalized': norm_ira})
    norm_ira.to_csv(f"{newname}.csv", index=False)
    return (len(eff_ref), max(eff_ref))


#enter your path here
path1 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\DATA-Ordered2.xlsx'
path2 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\700S1500.csv'
newname = '400F650_normalized'
headers = ['date', 'irradiance']

print(normalize_file(path2))
