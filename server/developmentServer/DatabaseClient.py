import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DatabaseConfigs import localhost_database_config
from DatabaseConfigs import remote_database_config
from Translator import DetectorUnitDataTranslator
from ORMBase import commonBase


class DatabaseClient:
    def __init__(self, config=localhost_database_config):
        self.session = None
        self.db_config = config
        self.engine = create_engine("mysql+pymysql://{}:{}@{}/{}".format(self.db_config.user,
                                                                         self.db_config.password,
                                                                         self.db_config.server_host,
                                                                         self.db_config.database))
        self.logger = logging.getLogger("Monitor_DB")
        self.translator = DetectorUnitDataTranslator()
        self.base = commonBase

    def init_tables(self):
        self.base.metadata.create_all(bind=self.engine)

    def make_session(self):
        self.session = sessionmaker(bind=self.engine)()

    def insert_photodiode_data(self, dataFilePath):
        try:
            self.make_session()
            ormList = self.translator.from_txt_to_orm(dataFilePath)
            for data in ormList:
                self.session.add(data)
            self.session.commit()
        except Exception as E:
            self.logger.exception(E)
            self.logger.exception('Lost connection to database')


if __name__ == '__main__':
    dbc = DatabaseClient(config=remote_database_config)
    dbc.init_tables()
    dbc.insert_photodiode_data("testData.txt")
