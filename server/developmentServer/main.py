import os
import pathlib
from datetime import datetime, timedelta
from DatabaseConfigs import remote_database_config
from DatabaseClient import DatabaseClient
import paramiko
import time

dbDir = os.path.dirname(os.path.abspath(__file__))
serverDir = "C:/SnowOptics/data"

TAGS = ["PD_", "IM_", "IML_"]


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


def listenForNewFiles(intervalInSeconds=8):
    print("...listening")
    pastFiles = loadPastFiles()

    newFiles = []
    while len(newFiles) == 0:
        newFiles = [f for f in loadCurrentFiles() if f not in pastFiles]
        time.sleep(1)

    # Time window for additional files to be added after the first batch is detected
    lastBatch = 0
    while len(newFiles) != lastBatch:
        print("Detected {} new files.".format(len(newFiles) - lastBatch))
        lastBatch = len(newFiles)
        currentFiles = loadCurrentFiles()
        newFiles = [f for f in currentFiles if f not in pastFiles]
        time.sleep(intervalInSeconds)

    return newFiles, currentFiles


def sendImages(files):
    print(".Sending {} Im: {}".format(len(files), [f.split(".")[0] for f in files]))

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect("74.15.144.100", port=250, username="jlbegin")
        sftp = ssh.open_sftp()
    except Exception as e:
        print("E.SSH: {}".format(type(e).__name__))
        return

    for fileName in files:
        sourcePath = os.path.join(serverDir, fileName)

        # timeObject = datetime.fromtimestamp(pathlib.Path(sourcePath).stat().st_ctime)
        # timeString = timeObject.strftime("%Y-%m-%d %H:%M:%S")
        # timeStampFile = os.path.join(os.path.dirname(serverDir), "times.temp")
        # with open(timeStampFile, "w+") as f:
        #     f.write("<p>Last frame: {}</p>".format(timeString))

        try:
            if "IM_" in fileName:
                sftp.put(sourcePath,
                         "/usr/share/grafana/public/img/highres.jpg")
                print("Updated Grafana High Res Image")
            elif "IML_" in fileName:
                sftp.put(sourcePath,
                         "/usr/share/grafana/public/img/lowres.jpg")
                print("Updated Grafana Low Res Image")

        except Exception as e:
            print("E.Send {} : {}".format(fileName, type(e).__name__))

    sftp.close()
    ssh.close()


def backTrackTime(filePath, index=0, delta=1):
    timeObject = datetime.fromtimestamp(pathlib.Path(filePath).stat().st_ctime)
    correctTime = timeObject - timedelta(seconds=57 * delta * index)
    shiftTime = correctTime + timedelta(minutes=4)  # opens at 6h56, not 7
    if shiftTime.hour < 7 or shiftTime.hour > 17:
        correctTime = correctTime - timedelta(hours=14)
    return correctTime


if __name__ == '__main__':
    # Ignore files already on the server
    # setPastFiles(loadCurrentFiles())

    while True:
        newFiles, currentFiles = listenForNewFiles()
        newFiles.sort(key=fileKey)

        dataFiles = [f for f in newFiles if "PD_" in f]
        highResImages = [f for f in newFiles if "IM_" in f]
        lowResImages = [f for f in newFiles if "IML_" in f]

        lastImages = [l[-1] for l in [highResImages, lowResImages] if l]
        if lastImages:
            sendImages(lastImages)

        try:
            dbc = DatabaseClient(remote_database_config)
            for i, file in enumerate(dataFiles):
                filePath = os.path.join(serverDir, file)
                timeStamp = backTrackTime(filePath, index=len(dataFiles) - (i + 1), delta=1)
                timeString = timeStamp.strftime("%Y-%m-%d %H:%M:%S")
                print(filePath, "at", timeString)
                dbc.add_detector_data(filePath, timeStamp)
                dbc.add_photodiode_power_data(filePath, timeStamp)
            for i, file in enumerate(highResImages):
                filePath = os.path.join(serverDir, file)
                timeStamp = backTrackTime(filePath, index=len(highResImages) - (i + 1), delta=60)
                timeString = timeStamp.strftime("%Y-%m-%d %H:%M:%S")
                print(filePath, "at", timeString)
                dbc.add_highres_image(filePath, timeStamp)
            for i, file in enumerate(lowResImages):
                filePath = os.path.join(serverDir, file)
                timeStamp = backTrackTime(filePath, index=len(lowResImages) - (i + 1), delta=1)
                timeString = timeStamp.strftime("%Y-%m-%d %H:%M:%S")
                print(filePath, "at", timeString)
                dbc.add_lowres_image(filePath, timeStamp)
            dbc.commit_data()
            setPastFiles(currentFiles)
        except Exception as e:
            print("DB Error: {}".format(type(e).__name__))
