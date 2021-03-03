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
    unit_id = Column(String(2))
    pd_id = Column(String(2))
    timeStamp = Column(DateTime)
    location = Column(String(1))
    height = Column(String(10))
    wavelength = Column(String(10))
    powerMean = Column(Float)
    powerSD = Column(Float)
    digitalNumberMean = Column(Float)
    digitalNumberSD = Column(Float)


class AllPhotodiodeDataORM(commonBase):
    __tablename__ = "AllPhotodiodeData2"

    id = Column(String(36), primary_key=True)
    timeStamp = Column(DateTime)

    mean_pd11_700nm_485mm_s = Column(Float)
    sd_pd11_700nm_485mm_s = Column(Float)
    mean_pd12_700nm_325mm_s = Column(Float)
    sd_pd12_700nm_325mm_s = Column(Float)
    mean_pd13_400nm_325mm_s = Column(Float)
    sd_pd13_400nm_325mm_s = Column(Float)
    mean_pd14_400nm_485mm_s = Column(Float)
    sd_pd14_400nm_485mm_s = Column(Float)
    mean_pd21_700nm_650mm_s = Column(Float)
    sd_pd21_700nm_650mm_s = Column(Float)
    mean_pd22_700nm_850mm_s = Column(Float)
    sd_pd22_700nm_850mm_s = Column(Float)
    mean_pd23_400nm_850mm_s = Column(Float)
    sd_pd23_400nm_850mm_s = Column(Float)
    mean_pd24_400nm_650mm_s = Column(Float)
    sd_pd24_400nm_650mm_s = Column(Float)
    mean_pd31_700nm_1200mm_s = Column(Float)
    sd_pd31_700nm_1200mm_s = Column(Float)
    mean_pd32_700nm_1000mm_s = Column(Float)
    sd_pd32_700nm_1000mm_s = Column(Float)
    mean_pd33_400nm_1000mm_s = Column(Float)
    sd_pd33_400nm_1000mm_s = Column(Float)
    mean_pd34_400nm_1200mm_s = Column(Float)
    sd_pd34_400nm_1200mm_s = Column(Float)
    mean_pd41_700nm_1550mm_s = Column(Float)
    sd_pd41_700nm_1550mm_s = Column(Float)
    mean_pd42_700nm_1375mm_s = Column(Float)
    sd_pd42_700nm_1375mm_s = Column(Float)
    mean_pd43_400nm_1375mm_s = Column(Float)
    sd_pd43_400nm_1375mm_s = Column(Float)
    mean_pd44_400nm_1550mm_s = Column(Float)
    sd_pd44_400nm_1550mm_s = Column(Float)
    mean_pd51_700nm_485mm_f = Column(Float)
    sd_pd51_700nm_485mm_f = Column(Float)
    mean_pd52_700nm_325mm_f = Column(Float)
    sd_pd52_700nm_325mm_f = Column(Float)
    mean_pd53_400nm_325mm_f = Column(Float)
    sd_pd53_400nm_325mm_f = Column(Float)
    mean_pd54_400nm_485mm_f = Column(Float)
    sd_pd54_400nm_485mm_f = Column(Float)
    mean_pd61_700nm_1200mm_f = Column(Float)
    sd_pd61_700nm_1200mm_f = Column(Float)
    mean_pd62_700nm_1000mm_f = Column(Float)
    sd_pd62_700nm_1000mm_f = Column(Float)
    mean_pd63_400nm_1000mm_f = Column(Float)
    sd_pd63_400nm_1000mm_f = Column(Float)
    mean_pd64_400nm_1200mm_f = Column(Float)
    sd_pd64_400nm_1200mm_f = Column(Float)
    mean_pd71_700nm_850mm_f = Column(Float)
    sd_pd71_700nm_850mm_f = Column(Float)
    mean_pd72_700nm_650mm_f = Column(Float)
    sd_pd72_700nm_650mm_f = Column(Float)
    mean_pd73_400nm_650mm_f = Column(Float)
    sd_pd73_400nm_650mm_f = Column(Float)
    mean_pd74_400nm_850mm_f = Column(Float)
    sd_pd74_400nm_850mm_f = Column(Float)
    mean_pd81_700nm_1375mm_f = Column(Float)
    sd_pd81_700nm_1375mm_f = Column(Float)
    mean_pd82_700nm_1550mm_f = Column(Float)
    sd_pd82_700nm_1550mm_f = Column(Float)
    mean_pd83_400nm_1550mm_f = Column(Float)
    sd_pd83_400nm_1550mm_f = Column(Float)
    mean_pd84_400nm_1375mm_f = Column(Float)
    sd_pd84_400nm_1375mm_f = Column(Float)


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




# All column name
# mean_pd11_700nm_485mm_s,
# sd_pd11_700nm_485mm_s,
# mean_pd12_700nm_325mm_s,
# sd_pd12_700nm_325mm_s,
# mean_pd13_400nm_325mm_s,
# sd_pd13_400nm_325mm_s,
# mean_pd14_400nm_485mm_s,
# sd_pd14_400nm_485mm_s,
# mean_pd21_700nm_650mm_s,
# sd_pd21_700nm_650mm_s,
# mean_pd22_700nm_850mm_s,
# sd_pd22_700nm_850mm_s,
# mean_pd23_400nm_850mm_s,
# sd_pd23_400nm_850mm_s,
# mean_pd24_400nm_650mm_s,
# sd_pd24_400nm_650mm_s,
# mean_pd31_700nm_1200mm_s,
# sd_pd31_700nm_1200mm_s,
# mean_pd32_700nm_1000mm_s,
# sd_pd32_700nm_1000mm_s,
# mean_pd33_400nm_1000mm_s,
# sd_pd33_400nm_1000mm_s,
# mean_pd34_400nm_1200mm_s,
# sd_pd34_400nm_1200mm_s,
# mean_pd41_700nm_1550mm_s,
# sd_pd41_700nm_1550mm_s,
# mean_pd42_700nm_1375mm_s,
# sd_pd42_700nm_1375mm_s,
# mean_pd43_400nm_1375mm_s,
# sd_pd43_400nm_1375mm_s,
# mean_pd44_400nm_1550mm_s,
# sd_pd44_400nm_1550mm_s,
# mean_pd51_700nm_485mm_f,
# sd_pd51_700nm_485mm_f,
# mean_pd52_700nm_325mm_f,
# sd_pd52_700nm_325mm_f,
# mean_pd53_400nm_325mm_f,
# sd_pd53_400nm_325mm_f,
# mean_pd54_400nm_485mm_f,
# sd_pd54_400nm_485mm_f,
# mean_pd61_700nm_1200mm_f,
# sd_pd61_700nm_1200mm_f,
# mean_pd62_700nm_1000mm_f,
# sd_pd62_700nm_1000mm_f,
# mean_pd63_400nm_1000mm_f,
# sd_pd63_400nm_1000mm_f,
# mean_pd64_400nm_1200mm_f,
# sd_pd64_400nm_1200mm_f,
# mean_pd71_700nm_850mm_f,
# sd_pd71_700nm_850mm_f,
# mean_pd72_700nm_650mm_f,
# sd_pd72_700nm_650mm_f,
# mean_pd73_400nm_650mm_f,
# sd_pd73_400nm_650mm_f,
# mean_pd74_400nm_850mm_f,
# sd_pd74_400nm_850mm_f,
# mean_pd81_700nm_1375mm_f,
# sd_pd81_700nm_1375mm_f,
# mean_pd82_700nm_1550mm_f,
# sd_pd82_700nm_1550mm_f,
# mean_pd83_400nm_1550mm_f,
# sd_pd83_400nm_1550mm_f,
# mean_pd84_400nm_1375mm_f,
# sd_pd84_400nm_1375mm_f,

