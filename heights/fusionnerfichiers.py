import pandas as pd
import os
import glob
from datetime import datetime as dt

def Exceltocsv(path, name, headers, rows=None, colums=None,):
    """read an Excel file and transform the useful data in a csv
    
    path: str of the path of the file
    name: name of the csv file
    headers: list of the names of the colums in the dataframe (must have the same number of colums entered)
    rows: int of the number of the rows we want to store (all by default)
    colums: str of the letter of the solums we want to store (all by default) -- EX: 'A,K' (colums A and K) 
                                                                                     'A-K' (colums A to K)

    return the data and save a csv
    """
    data = pd.read_excel(path, names=headers, usecols=colums, nrows=rows, na_values='na')
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
    #takes the files and put them in a list
    files_joined = os.path.join(path, f"*{common}*.csv")
    list_files = glob.glob(files_joined)
    #join the files in a dataframe panda
    dataFrame = pd.concat(map(pd.read_csv, list_files))
    #save the dataframe in a csv
    dataFrame.to_csv(f"{newname}.csv", index=False)
    return dataFrame

def renamefiles_asDanwishes(path):
    """rename all the file of a certain folder with the format "yyyymmdd-*". If a file with its 'new name'
    got the same name of another file (for example an older version), an exception will stop the programm
    and you must delete one of the version to continue (no duplicate will be created!)

    path: str of the path to the folder
    (nothing is return)
    """
    names = os.listdir(path)
    #Here I assume that the new files put in the folder were created/updated today, you can change it as you wish
    date = dt.today().strftime("%Y%m%d")
    for name in names:
        nfc = os.path.join(path, name)
        #I know that I have only files of this year in my folder and no "ID" contains "2022" in the name, except those who are already renamed
        #you must add other exceptions for other years if that is the case
        if "2022" not in name:
            os.rename(nfc, os.path.join(path, f"{date}-" + name))

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

def stripcolums(path, newname, colum):
    """delete colums of the file chosen
    
    path: str of the path of the file
    newname: name of the file modified
    colum: list of the lower and upper bound of the colums we want to keep

    return the dataframe and save csv
    """
    df = pd.read_csv(path, header=0)
    df = df.iloc[:, colum[0]:colum[1]]
    df.to_csv(f"{newname}.csv", index=False)
    return df

#enter your path here
path = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\all_heightsAM.csv'
