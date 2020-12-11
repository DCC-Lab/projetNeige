import os
import pathlib
from datetime import datetime, timedelta
from DatabaseConfigs import remote_database_config
from DatabaseClient import DatabaseClient
import time

dbDir = os.path.dirname(os.path.abspath(__file__))
serverDir = "C:/SnowOptics/data"

TAGS = ["PD_"]


def loadPastFiles():
    with open(os.path.join(dbDir, "fileHistory.txt"), "r") as f:
        files = [l.replace("\n", "") for l in f.readlines()]
    return files


def setPastFiles(files: list):
    with open(os.path.join(dbDir, "fileHistory.txt"), "w+") as f:
        f.write('\n'.join(files) + '\n')


def loadCurrentFiles():
    return [f for f in list(os.walk(serverDir))[0][2] if any(tag in f for tag in TAGS)]


def fileKey(filename: str):
    return int(filename.split(".")[0].split("_")[1])


def listenForNewFiles(intervalInSeconds=4):
    print("...listening")
    pastFiles = loadPastFiles()

    newFiles = []
    while len(newFiles) == 0:
        newFiles = [f for f in loadCurrentFiles() if f not in pastFiles]
        time.sleep(intervalInSeconds)

    # Time window for additional files to be added after the first batch is detected
    lastBatch = 0
    while len(newFiles) != lastBatch:
        print("Detected {} new files.".format(len(newFiles) - lastBatch))
        lastBatch = len(newFiles)
        currentFiles = loadCurrentFiles()
        newFiles = [f for f in currentFiles if f not in pastFiles]
        time.sleep(intervalInSeconds)

    return newFiles, currentFiles


if __name__ == '__main__':
    # Ignore files already on the server
    setPastFiles(loadCurrentFiles())

    while True:
        newFiles, currentFiles = listenForNewFiles()
        newFiles.sort(key=fileKey)

        try:
            dbc = DatabaseClient(remote_database_config)
            for i, file in enumerate(newFiles):
                filePath = os.path.join(serverDir, file)
                timeObject = datetime.fromtimestamp(pathlib.Path(filePath).stat().st_ctime)
                delta = len(newFiles) - (i+1)
                dbc.insert_photodiode_data(filePath, timeObject - timedelta(minutes=1 * delta))
            setPastFiles(currentFiles)
        except Exception as e:
            print("DB Error: {}".format(type(e).__name__))
