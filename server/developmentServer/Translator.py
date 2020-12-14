import uuid
from dataclasses import dataclass
from ORM import DetectorUnitDataORM, LowResolutionFeedORM, HighResolutionFeedORM, PhotodiodeDataORM
import csv


class Translator:

    @staticmethod
    def from_txt_to_power_ORM(filePath, timeStamp):
        ORMList = []
        calibrationList = []
        with open('candle_calibration_info.csv', newline='') as csvFile:
            csvReader = csv.reader(csvFile, delimiter=',')
            next(csvReader, None)
            for row in csvReader:
                calibrationList.append(row)

        with open(filePath, 'r') as f:
            rawData = [line.rstrip().split(sep=" ") for line in f]
            rawData = [rawData[i:i + 6] for i in range(0, len(rawData), 6)]
            for i, unitRawData in enumerate(rawData):

                for j, statData in enumerate(unitRawData):
                    if j < 4:
                        actualIndex = i * 4 + j
                        statData = [None if d == 'nan' else d for d in statData]
                        translatedDict = {}
                        translatedDict["location"] = str(calibrationList[actualIndex][-1])
                        translatedDict["height"] = float(calibrationList[actualIndex][-3])
                        translatedDict["wavelength"] = float(calibrationList[actualIndex][-2])
                        translatedDict["digitalNumberMean"] = float(statData[0])
                        translatedDict["digitalNumberSD"] = float(statData[1])
                        translatedDict["powerMean"] = ((float(statData[0]) * float(calibrationList[actualIndex][2])) + float(calibrationList[actualIndex][3]))
                        translatedDict["powerSD"] = (float(statData[1]) * float(calibrationList[actualIndex][2]))

                        ORMList.append(PhotodiodeDataORM(id=str(uuid.uuid4()), timeStamp=timeStamp, **translatedDict))

            return ORMList

    @staticmethod
    def from_txt_to_detector_ORM(filePath, timeStamp):
        ORMList = []

        timeString = timeStamp.strftime("%Y-%m-%d %H:%M:%S")
        print(filePath, "at", timeString)

        with open(filePath, 'r') as f:
            rawData = [line.rstrip().split(sep=" ") for line in f]
            rawData = [rawData[i:i + 6] for i in range(0, len(rawData), 6)]
            # print(rawData)
            for i, unitRawData in enumerate(rawData):
                translatedDict = {"unitID": str(i + 1)}
                if i < 4:
                    translatedDict["relatedClusterName"] = "Chrubs"
                else:
                    translatedDict["relatedClusterName"] = "Field"

                for j, statData in enumerate(unitRawData):
                    statData = [None if d == 'nan' else d for d in statData]
                    if j == 0:
                        translatedDict["pd{}DigitalNumberMean".format(1)] = statData[0]
                        translatedDict["pd{}DigitalNumberSd".format(1)] = statData[1]

                    elif j == 1:
                        translatedDict["pd{}DigitalNumberMean".format(4)] = statData[0]
                        translatedDict["pd{}DigitalNumberSd".format(4)] = statData[1]

                    elif j == 2:
                        translatedDict["pd{}DigitalNumberMean".format(2)] = statData[0]
                        translatedDict["pd{}DigitalNumberSd".format(2)] = statData[1]

                    elif j == 3:
                        translatedDict["pd{}DigitalNumberMean".format(3)] = statData[0]
                        translatedDict["pd{}DigitalNumberSd".format(3)] = statData[1]

                    elif j == 4:
                        translatedDict["temperatureMean"] = statData[0]
                        translatedDict["temperatureSd"] = statData[1]

                    elif j == 5:
                        translatedDict["humidityMean"] = statData[0]
                        translatedDict["humiditySd"] = statData[1]

                ORMList.append(DetectorUnitDataORM(id=str(uuid.uuid4()), **translatedDict, timeStamp=timeStamp))

            return ORMList

    @staticmethod
    def from_image_to_lowres_ORM(filepath, timestamp):
        ORMList = []
        with open(filepath, 'rb') as file:
            binaryData = file.read()
            ORMList.append(LowResolutionFeedORM(id=str(uuid.uuid4()), timeStamp=timestamp, image=binaryData))

        return ORMList


    @staticmethod
    def from_image_to_highres_ORM(self, filepath, timestamp):
        ORMList = []

        with open(filepath, 'rb') as file:
            binaryData = file.read()
            ORMList.append(HighResolutionFeedORM(id=str(uuid.uuid4()), timeStamp=timestamp, image=binaryData))

        return ORMList


if __name__ == "__main__":
    import csv

    with open('candle_calibration_info.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        print(csvreader)
