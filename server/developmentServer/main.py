import os
dbDir = os.path.dirname(os.path.abspath(__file__))
serverDir = "C:/SnowOptics/data"
# import sys
# sys.path.append(dbDir)
from DatabaseConfigs import remote_database_config
from DatabaseClient import DatabaseClient
import time


def loadPastFiles():
    with open(os.path.join(dbDir, "fileHistory.txt"), "r") as f:
        files = [l.replace("\n", "") for l in f.readlines()]
    return files


def setPastFiles(files: list):
    with open(os.path.join(dbDir, "fileHistory.txt"), "w+") as f:
        f.write('\n'.join(files) + '\n')


def loadCurrentFiles():
    return list(os.walk(serverDir))[0][2]


def listenForNewFiles(intervalInSeconds=5):
    pastFiles = loadPastFiles()
    newFiles = []

    while len(newFiles) == 0:
        newFiles = [f for f in loadCurrentFiles() if f not in pastFiles]
        time.sleep(intervalInSeconds)

    # This leaves a time window for additional files to be added after the first batch is detected
    currentFiles = loadCurrentFiles()
    setPastFiles(currentFiles)

    return [f for f in currentFiles if f not in pastFiles]


if __name__ == '__main__':
    # Used to not ignore files already on the server
    setPastFiles(loadCurrentFiles())

    while True:
        files = listenForNewFiles()
        dbc = DatabaseClient(remote_database_config)
        for file in files:
            dbc.insert_photodiode_data(os.path.join(serverDir, file))
