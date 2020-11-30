import uuid
from typing import Dict
from .ORM import PhotodiodeDataORM


class PhotodiodeDataTranslator:
    @staticmethod
    def from_data_to_orm(raw_data) -> PhotodiodeDataORM:
        translated_dict = {}
        translated_dict = raw_data
        return PhotodiodeDataORM(id=str(uuid.uuid4()), **translated_dict)

    def from_txt_to_orm(self, filePath):
        with open(filePath, 'r') as f:
            rawData = [line.rstrip() for line in f]

            return PhotodiodeDataORM(id=str(uuid.uuid4()))