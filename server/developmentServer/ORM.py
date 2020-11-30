import uuid
from sqlalchemy import Column, String, Integer, Date, Time, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base


class DetectorUnitORM(declarative_base()):
    __tablename__ = "DetectorUnits"
    id = Column(String(36), primary_key=True)
    relatedClusterID = Column(String(36))
    relatedSystemID = Column(String(36))
    location = Column(String(36))


class DetectorUnitDataORM(declarative_base()):
    __tablename__ = "DetectorUnits"
    id = Column(String(36), primary_key=True)
    unitID = Column(String(36))
    relatedClusterName = Column(String(36))
    timeStamp = Column(DateTime)
    pd1DigitalNumberMean = Column(Float)
    pd1DigitalNumberSd = Column(Float)
    pd2DigitalNumberMean = Column(Float)
    pd2DigitalNumberSd = Column(Float)
    pd3DigitalNumberMean = Column(Float)
    pd3DigitalNumberSd = Column(Float)
    pd4DigitalNumberMean = Column(Float)
    pd4DigitalNumberSd = Column(Float)
    temperatureMean = Column(Float)
    temperatureSd = Column(Float)
    humidityMean = Column(Float)
    humiditySd = Column(Float)

class PhotodiodeDataORM(declarative_base()):
    __tablename__ = "PhotodiodeData"
    dataID = Column(String(36), primary_key=True)
    photodiodeID = Column(Integer)
    photodiodeBand = Column(String(36))
    relatedUnitID = Column(Integer)
    relatedClusterID = Column(Integer)
    relatedSystemID = Column(Integer)
    timeStamp = Column(DateTime)
    DigitalNumberMean = Column(Integer)
    DigitalNumberSd = Column(Integer)

    correctedValue = Column(String)


if __name__ == '__main__':
    data_dict = {}
    sensor_data = PhotodiodeDataORM(id=str(uuid.uuid4()), **data_dict)
