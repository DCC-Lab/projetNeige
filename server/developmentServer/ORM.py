from sqlalchemy import Column, String, Integer, Date, Time, DateTime, Float
from sqlalchemy.dialects.mysql import MEDIUMBLOB
from ORMBase import commonBase


class DetectorUnitDataORM(commonBase):
    __tablename__ = "DetectorUnitsData"
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

class PhotodiodeDataORM(commonBase):
    __tablename__ = "PhotodiodeData"
    id = Column(String(36), primary_key=True)
    timeStamp = Column(DateTime)
    location = Column(String(1))
    height = Column(String(10))
    wavelength = Column(String(10))
    powerMean = Column(Float)
    powerSD = Column(Float)
    digitalNumberMean = Column(Float)
    digitalNumberSD = Column(Float)

class LowResolutionFeedORM(commonBase):
    __tablename__ = "lowResolutionFeed"
    id = Column(String(36), primary_key=True)
    timeStamp = Column(DateTime)
    image = Column(MEDIUMBLOB)


class HighResolutionFeedORM(commonBase):
    __tablename__ = "highResolutionFeed"
    id = Column(String(36), primary_key=True)
    timeStamp = Column(DateTime)
    image = Column(MEDIUMBLOB)




