import pandas as pd
import os
import glob
from datetime import datetime as dt

def joincsvfiles(path, common, newname):
    """join csv files with a similar name in alphabetic order
    
    path: str of the path of the file
    common: str of what is similar in all the files you want to join (at the beginning of the name)
    newname: name of the new file

    return csv of the dataframe
    """
    #takes the files and put them in a list
    files_joined = os.path.join(path, f"{common}*.csv")
    list_files = glob.glob(files_joined)
    #join the files in a dataframe panda
    dataFrame = pd.concat(map(pd.read_csv, list_files), ignore_index=True)
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


#enter your path here
path = ''
renamefiles_asDanwishes(path)