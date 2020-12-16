from main import *


def timeStampKey(filename: str):
    TS = datetime.fromtimestamp(pathlib.Path(os.path.join(serverDir, filename)).stat().st_ctime)
    return int(TS.timestamp())


if __name__ == '__main__':
    allFiles = loadCurrentFiles()
    allFiles.sort(key=timeStampKey)

    # create batches
    batches = []
    tempBatch = [allFiles[0]]
    for file in allFiles[1:]:
        lastFile = tempBatch[-1]
        lastTS = datetime.fromtimestamp(pathlib.Path(os.path.join(serverDir, lastFile)).stat().st_ctime)
        liveTS = datetime.fromtimestamp(pathlib.Path(os.path.join(serverDir, file)).stat().st_ctime)
        timeDiff = liveTS - lastTS
        if timeDiff.total_seconds() < 25:
            tempBatch.append(file)
        else:
            batches.append(tempBatch)
            tempBatch = [file]
    batches.append(tempBatch)

    dbc = DatabaseClient(remote_database_config)
    for i, batch in enumerate(batches):
        batch.sort(key=fileKey)
        print(">>> Batch {}/{}".format(i+1, len(batches)))
        print("{} files".format(len(batch)))

        dataFiles = [f for f in batch if "PD_" in f]
        highResImages = [f for f in batch if "IM_" in f]
        lowResImages = [f for f in batch if "IML_" in f]

        try:
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
                dbc.add_highres_image(filePath, backTrackTime(filePath, index=len(highResImages) - (i + 1), delta=60))
                timeString = timeStamp.strftime("%Y-%m-%d %H:%M:%S")
                print(filePath, "at", timeString)
            for i, file in enumerate(lowResImages):
                filePath = os.path.join(serverDir, file)
                timeStamp = backTrackTime(filePath, index=len(lowResImages) - (i + 1), delta=1)
                dbc.add_lowres_image(filePath, backTrackTime(filePath, index=len(lowResImages) - (i + 1), delta=1))
                timeString = timeStamp.strftime("%Y-%m-%d %H:%M:%S")
                print(filePath, "at", timeString)
        except Exception as e:
            print("DB Error: {}".format(e))
    dbc.commit_data()
