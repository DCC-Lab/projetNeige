import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .DatabaseConfigs import localhost_database_config
from .ORM import PhotodiodeDataORM
from .ORM import DetectorUnitORM


class DatabaseClient:
    def __init__(self):
        self.session = None
        self.db_config = localhost_database_config
        self.engine = create_engine("mysql+mysqlconnector://{}:{}@{}/{}".format(self.db_config.user,
                                                                                self.db_config.password,
                                                                                self.db_config.server_host,
                                                                                self.db_config.database))
        self.logger = logging.getLogger("Monitor_DB")

    def make_session(self):
        self.session = sessionmaker(bind=self.engine)()

    def insert_photodiode_data(self, data_dict):
        try:
            self.make_session()
            self.session.add(PhotodiodeDataORM.from_data_to_orm(data_dict))
            self.session.commit()
        except Exception as E:
            self.logger.exception(E)
            self.logger.exception('Lost connection to database')


if __name__ == '__main__':
    pass

