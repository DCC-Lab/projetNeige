import uuid
from sqlalchemy import Column, String, Integer, Date, Time, DateTime, Float
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

