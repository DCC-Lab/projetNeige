import uuid
from ORM import PhotodiodeDataORM
from ORM import DetectorUnitDataORM


class PhotodiodeDataTranslator:
    @staticmethod
    def from_data_to_orm(raw_data) -> PhotodiodeDataORM:
        translated_dict = raw_data
        return PhotodiodeDataORM(id=str(uuid.uuid4()), **translated_dict)

    def from_txt_to_orm(self, filePath):
        translatedDict = {}
        with open(filePath, 'r') as f:
            rawData = [line.rstrip() for line in f]
            rawData = [rawData[i:i+7] for i in range(0, len(rawData), 7)]
            for i, unitRawData in enumerate(rawData):
                for j, statData in enumerate(unitRawData):

                    translatedDict["photodiodeID"] = f"{i}"
            return PhotodiodeDataORM(id=str(uuid.uuid4()), **translatedDict)


class DetectorUnitDataTranslator:

    def from_txt_to_orm(self, filePath):
        ORMList = []

        with open(filePath, 'r') as f:
            rawData = [line.rstrip().split(sep=" ") for line in f]
            rawData = [rawData[i:i + 6] for i in range(0, len(rawData), 6)]
            print(rawData)
            for i, unitRawData in enumerate(rawData):
                translatedDict = {"unitID": str(i + 1)}
                if i < 4:
                    translatedDict["relatedClusterName"] = "Chrubs"
                else:
                    translatedDict["relatedClusterName"] = "Field"
                    
                for j, statData in enumerate(unitRawData):
                    if j <= 3:
                        translatedDict["pd{}DigitalNumberMean".format(j+1)] = statData[0]
                        translatedDict["pd{}DigitalNumberSd".format(j+1)] = statData[1]
                        
                    elif j == 4:
                        translatedDict["temperatureMean"] = statData[0]
                        translatedDict["temperatureSd"] = statData[1]

                    elif j == 5:
                        translatedDict["humidityMean"] = statData[0]
                        translatedDict["humiditySd"] = statData[1]

                ORMList.append(DetectorUnitDataORM(id=str(uuid.uuid4()), **translatedDict, timeStamp="1900-02-11 01:01:01"))

            return ORMList


if __name__ == "__main__":
    translator = DetectorUnitDataTranslator()
    ormList = translator.from_txt_to_orm("testData.txt")
    print(ormList[0].__dict__)
    print(ormList[1].__dict__)
    print(ormList[2].__dict__)
    print(ormList[3].__dict__)
    print(ormList[4].__dict__)
    print(ormList[5].__dict__)
    print(ormList[6].__dict__)
    print(ormList[7].__dict__)
