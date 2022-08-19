from typing import Set
from certifi import where
from dcclab.database import Database
import pandas as pd
import numpy as np

# Join values with same date
"""UPDATE crn4 t1, (
    SELECT DISTINCT `datetime`, weather_median 
    FROM crn4 
    WHERE weather_median IS NOT NULL
) t2 SET t1.weather_median = t2.weather_median
WHERE t1.datetime = t2.datetime;"""

# Modify values of one table according to another table
"""UPDATE table1, table2
SET 
    table.col1 = table2.col1
WHERE
    table2.date.date = cast(table1.datetime AS DATE);"""

class NeigeDB(Database):
    def __init__(self, databaseURL=None):
        if databaseURL is None:
            databaseURL = "mysql+ssh://dcclab@cafeine2.crulrg.ulaval.ca:cafeine3.crulrg.ulaval.ca/dcclab@neige"
        super().__init__(databaseURL=databaseURL)

    def getvaluesfromtable(self, table, columns, date=True):
        """Get values from a table in the database.
        
        table (str): Name of the table.
        columns (list): List of columns to get.
        date (bool): If True, the first column is transformed in datetime format.
        
        Returns a pandas dataframe.
        """
        self.execute("SELECT * FROM {}".format(table))
        df = pd.DataFrame(self.fetchAll())
        df = df.loc[:, columns]
        df = df.dropna()
        ## Work in progress to keep the NaN values in the dataframe
        # a = df.index[0]
        # for b in df.index[1:]:
        #     if a+1 == b:
        #         continue
        #     else:
        #         df.loc[a+1, columns[1:]] = np.nan
        #         print(a)
        #     a = b
            
        df = df.reset_index(drop=True)
        if date:
            df[columns[0]] = pd.to_datetime(df[columns[0]])
        return df


if __name__ == "__main__":
    db = NeigeDB()
    db.getvaluesfromtable("SnowSiteData", ['datetime', "weather_median"])
    pass