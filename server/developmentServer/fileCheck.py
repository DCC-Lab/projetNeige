import datetime as dt
import os
import socket
from os import listdir
from os.path import isfile, join, dirname, realpath
from DatabaseClient import DatabaseClient
from DatabaseConfigs import internal_databse_config, remote_database_config, localhost_database_config
import pathlib
import argparse

dataFolderPath = join(dirname(realpath(__file__)), "data")


class FileChecker:
    def __init__(self, startDate=None, stopDate=None, config=internal_databse_config):
        self.dbc = DatabaseClient(config=config)
        self.monitorStopDate = None
        self.startDate = startDate
        self.stopDate = stopDate
        self.missingDates = []
        self.update_time()
        pathlib.Path(dataFolderPath).mkdir(parents=True, exist_ok=True)

    def execute_file_monitoring(self):
        self.update_time()
        self.check_missing_files()
        self.get_missing_files()

    def check_missing_files(self):
        dates = [dt.datetime.strptime(f.replace(".csv", ""), "%Y-%m-%d").date() for f in listdir(dataFolderPath) if
                 isfile(join(dataFolderPath, f)) and ".csv" in f]
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
                file.write(
                    "id, unitID, photodiodeID, timeStamp, location, height, wavelength, powerMean, powerSD, digitalNumberMean, digitalNumberSD")
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
            command = "SELECT * FROM PhotodiodeData WHERE timeStamp BETWEEN '{}' AND '{}' ORDER BY timeStamp".format(
                minDate, maxDate)
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
            command = "SELECT * FROM PhotodiodeData WHERE CAST(timeStamp as time) BETWEEN '{}' AND '{}' AND timeStamp BETWEEN '{}' AND '{}' ORDER BY timeStamp".format(
                minTime, maxTime, minDate, maxDate)
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
    parser = argparse.ArgumentParser()
    gIP = parser.add_argument_group(title='IP options')
    mxgIP = gIP.add_mutually_exclusive_group(required=True)
    mxgIP.add_argument("-r", "--remote", help="Get remote ip configuration", action="store_true")
    mxgIP.add_argument("-l", "--local", help="Get local ip configuration", action="store_true")
    mxgIP.add_argument("-i", "--internal", help="Get internal ip configuration", action="store_true")

    gF = parser.add_argument_group(title='Functions')
    mxgF = gF.add_mutually_exclusive_group(required=False)
    mxgF.add_argument("--check", help="Check if daily file are correctly stored and download them to multiple .csv files", action="store_true", required=False)
    mxgF.add_argument("--make", nargs=4, metavar=('d1', 'd2', 't1', 't2'),
                      help=' startDate(Y-m-d), endDate, startTime(H:M:S), endTime, Make data file with certain span to a single .csv file', type=str)

    args = parser.parse_args()

    config = None
    if args.remote:
        config = remote_database_config
    elif args.local:
        config = localhost_database_config
    elif args.internal:
        config = internal_databse_config

    try:
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        a_socket.settimeout(3)
        location = (config.server_host, config.server_port)
        result_of_check = a_socket.connect_ex(location)

        if result_of_check != 0:
            print(f"TCP ERROR {result_of_check}")

        if result_of_check == 0:
            print("Host {} reachable and port {} is open".format(config.server_host, config.server_port))

        elif result_of_check == 10061:
            print("Host {} reachable but actively refused connection on port {}.".format(config.server_host, config.server_port))

        else:
            print("Host {} is not reachable or port {} has dropped packed.".format(config.server_host, config.server_port))
            raise Exception

        fc = FileChecker(startDate=dt.date(2020, 12, 3), stopDate=dt.date.today(), config=config)

    except Exception as e:
        print(e)

    if args.make:
        try:
            fc.make_data_file_span(args.make[0], args.make[1], args.make[2], args.make[3])
            print("File generation successful.")

        except Exception as e:
            print("FAILED: {}".format(e))

    elif args.check:
        fc.check_missing_files()

    else:
        pass


