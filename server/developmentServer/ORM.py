import uuid
from sqlalchemy import Column, String, Integer, Date, Time
from sqlalchemy.ext.declarative import declarative_base


class DetectorUnitORM(declarative_base):
    __tablename__ = "DetectorUnits"
    id = Column(String(36), primary_key=True)
    relatedClusterID = Column(String(36))
    relatedSystemID = Column(String(36))
    location = Column(String(36))


class PhotodiodeDataORM(declarative_base):
    __tablename__ = "PhotodiodeData"
    dataID = Column(String(36), primary_key=True)
    photodiodeID = Column(Integer)
    photodiodeBand = Column(String(36))
    relatedUnitID = Column(Integer)
    relatedClusterID = Column(Integer)
    relatedSystemID = Column(Integer)
    date = Column(Date)
    time = Column(Time)
    rawDigitalNumber = Column(Integer)
    correctedValue = Column(String)


if __name__ == '__main__':
    data_dict = {}
    sensor_performance_orm = PhotodiodeDataORM(id=str(uuid.uuid4()), **data_dict)
