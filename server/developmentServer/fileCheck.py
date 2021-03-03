import datetime as dt
import os
from os import listdir
from os.path import isfile, join, dirname, realpath
from DatabaseClient import DatabaseClient
from DatabaseConfigs import internal_databse_config

dataFolderPath = join(dirname(realpath(__file__)), "data")


class FileChecker:
    def __init__(self, startDate=None, stopDate=None):
        self.dbc = DatabaseClient(config=internal_databse_config)
        self.monitorStopDate = None
        self.startDate = startDate
        self.stopDate = stopDate
        self.missingDates = []
        self.update_time()

    def execute_file_monitoring(self):
        self.update_time()
        self.check_missing_files()
        self.get_missing_files()

    def check_missing_files(self):
        dates = [dt.datetime.strptime(f.replace(".csv", ""), "%Y-%m-%d").date() for f in listdir(dataFolderPath) if isfile(join(dataFolderPath, f)) and ".csv" in f]
        date_set = set(self.startDate + dt.timedelta(x) for x in range((self.monitorStopDate - self.startDate).days))
        self.missingDates = sorted(date_set - set(dates))

    def update_time(self):
        todayDate = dt.date.today()
        if todayDate <= self.stopDate:
            self.monitorStopDate = todayDate
        else:
            self.monitorStopDate = self.stopDate

    def get_missing_files(self):
        for missingDate in self.missingDates:
            with open("{}{}{}.csv".format(dataFolderPath, os.sep, missingDate), "w") as file:
                file.write("id, unitID, photodiodeID, timeStamp, location, height, wavelength, powerMean, powerSD, digitalNumberMean, digitalNumberSD")
                table = self.get_missing_data(missingDate)
                for row in table:
                    file.write("\n")
                    for element in row:
                        file.write(str(element))
                        file.write(",")

    def get_missing_data(self, date):
        minDate = date.strftime("%Y-%m-%d")
        maxDate = (date + dt.timedelta(days=1)).strftime("%Y-%m-%d")
        print("Requesting for missing:", minDate, maxDate)
        rows = []
        with self.dbc.engine.connect() as conn:
            command = "SELECT * FROM PhotodiodeData WHERE timeStamp BETWEEN '{}' AND '{}' ORDER BY timeStamp".format(minDate, maxDate)
            conn.execute('USE projetneigedb')
            rs = conn.execute(command)
            for row in rs.fetchall():
                row = self.formatPhotodiodeRow(list(row))
                rows.append(row)

        return rows

    def make_all_data_file(self):
        rows = []
        with self.dbc.engine.connect() as conn:
            command = "SELECT * FROM PhotodiodeData WHERE CAST(timeStamp as time) BETWEEN '10:00:00' AND '15:00:00' ORDER BY timeStamp;"
            conn.execute('USE projetneigedb')
            rs = conn.execute(command)
            for row in rs.fetchall():
                row = self.formatPhotodiodeRow(list(row))
                rows.append(row)

        with open("{}{}{}.csv".format(dataFolderPath, os.sep, "allData"), "w") as file:
            file.write(
                "id, unitID, photodiodeID, timeStamp, location, height, wavelength, powerMean, powerSD, digitalNumberMean, digitalNumberSD")

            for row in rows:
                file.write("\n")
                for element in row:
                    file.write(str(element))
                    file.write(",")

    def make_data_file_span(self, minDate, maxDate, minTime, maxTime):
        rows = []
        with self.dbc.engine.connect() as conn:
            command = "SELECT * FROM PhotodiodeData WHERE CAST(timeStamp as time) BETWEEN '{}' AND '{}' AND timeStamp BETWEEN '{}' AND '{}' ORDER BY timeStamp".format(minTime, maxTime, minDate, maxDate)
            conn.execute('USE projetneigedb')
            rs = conn.execute(command)
            for row in rs.fetchall():
                row = self.formatPhotodiodeRow(list(row))
                rows.append(row)

        with open("{}{}{}-{}.csv".format(dataFolderPath, os.sep, minDate, maxDate), "w") as file:
            file.write(
                "id, unitID, photodiodeID, timeStamp, location, height, wavelength, powerMean, powerSD, digitalNumberMean, digitalNumberSD")

            for row in rows:
                file.write("\n")
                for element in row:
                    file.write(str(element))
                    file.write(",")

    @staticmethod
    def formatPhotodiodeRow(row):
        row[1] = int(row[1])
        row[2] = int(row[2])
        row[3] = row[3].strftime("%Y-%m-%d %H:%M:%S")
        row[5] = float(row[5])
        row[6] = int(row[6])
        return row


if __name__ == "__main__":
    fc = FileChecker(startDate=dt.date(2020, 12, 3), stopDate=dt.date(2021, 4, 1))
    a = 1
    if a == 0:
        while 1:
            fc.execute_file_monitoring()
    elif a == 1:
        fc.make_data_file_span("2021-02-02", "2021-03-02", "10:00:00", "14:00:00")
