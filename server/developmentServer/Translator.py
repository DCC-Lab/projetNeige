import uuid
import pathlib
import datetime
from ORM import DetectorUnitDataORM


class DetectorUnitDataTranslator:

    def from_txt_to_orm(self, filePath, timeStamp):
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
                    if j <= 3:
                        translatedDict["pd{}DigitalNumberMean".format(j+1)] = statData[0]
                        translatedDict["pd{}DigitalNumberSd".format(j+1)] = statData[1]
                        
                    elif j == 4:
                        translatedDict["temperatureMean"] = statData[0]
                        translatedDict["temperatureSd"] = statData[1]

                    elif j == 5:
                        translatedDict["humidityMean"] = statData[0]
                        translatedDict["humiditySd"] = statData[1]

                ORMList.append(DetectorUnitDataORM(id=str(uuid.uuid4()), **translatedDict, timeStamp=timeStamp))

            return ORMList



if __name__ == "__main__":
    translator = DetectorUnitDataTranslator()
    ormList = translator.from_txt_to_orm("testData.txt")
