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


# deprecated
def sendImages(files):
    print(".Sending {}: {}".format(len(files), [f.split(".")[0] for f in files]))

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect("70.55.117.196", port=250, username="jlbegin")
        sftp = ssh.open_sftp()
    except Exception as e:
        print("E.SSH: {}".format(type(e).__name__))
        return

    for fileName in files:
        sourcePath = os.path.join(serverDir, fileName)

        timeObject = datetime.fromtimestamp(pathlib.Path(sourcePath).stat().st_ctime)
        timeString = timeObject.strftime("%Y-%m-%d %H:%M:%S")
        timeStampFile = os.path.join(os.path.dirname(serverDir), "times.temp")
        with open(timeStampFile, "w+") as f:
            f.write("<p>Last frame: {}</p>".format(timeString))

        try:
            if "IM_" in fileName:
                sftp.put(sourcePath,
                         "/usr/share/grafana/public/img/highres.jpg")
                sftp.put(timeStampFile,
                         "/usr/share/grafana/public/img/highresTimestamp.html")
                print("Sent High Res Image")
            elif "IML_" in fileName:
                sftp.put(sourcePath,
                         "/usr/share/grafana/public/img/lowres.jpg")
                sftp.put(timeStampFile,
                         "/usr/share/grafana/public/img/lowresTimestamp.html")
                print("Sent Low Res Image")

        except Exception as e:
            print("E.Send {} : {}".format(fileName, type(e).__name__))

    sftp.close()
    ssh.close()


if __name__ == '__main__':
    # Ignore files already on the server
    setPastFiles(loadCurrentFiles())

    while True:
        newFiles, currentFiles = listenForNewFiles()

        imageFiles = [f for f in newFiles if "PD_" not in f]
        dataFiles = [f for f in newFiles if "PD_" in f]
        dataFiles.sort(key=fileKey)
        try:
            dbc = DatabaseClient(remote_database_config)
            for i, file in enumerate(dataFiles):
                filePath = os.path.join(serverDir, file)
                timeObject = datetime.fromtimestamp(pathlib.Path(filePath).stat().st_ctime)
                delta = len(dataFiles) - (i+1)
                dbc.add_detector_data(filePath, timeObject - timedelta(minutes=1 * delta))
            for file in imageFiles:
                filePath = os.path.join(serverDir, file)
                timeObject = datetime.fromtimestamp(pathlib.Path(filePath).stat().st_ctime)
                if "IM_" in file:
                    dbc.add_highres_image(filePath, timeObject)
                    print("Sent High Res Image")
                elif "IML_" in file:
                    dbc.add_lowres_image(filePath, timeObject)
                    print("Sent Low Res Image")
            dbc.commit_data()
            setPastFiles(currentFiles)
        except Exception as e:
            print("DB Error: {}".format(type(e).__name__))
