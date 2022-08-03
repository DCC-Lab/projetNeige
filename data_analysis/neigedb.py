from typing import Set
from certifi import where
from dcclab.database import *
db = SpectraDB()


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