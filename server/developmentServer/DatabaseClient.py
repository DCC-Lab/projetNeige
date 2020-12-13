import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table
from DatabaseConfigs import localhost_database_config
from DatabaseConfigs import remote_database_config
from Translator import Translator
from ORM import LowResolutionFeedORM, HighResolutionFeedORM
from ORMBase import commonBase, localBase


class DatabaseClient:
    def __init__(self, config=localhost_database_config):
        self.session = None
        self.db_config = config
        self.engine = create_engine("mysql+pymysql://{}:{}@{}/{}".format(self.db_config.user,
                                                                         self.db_config.password,
                                                                         self.db_config.server_host,
                                                                         self.db_config.database))
        self.logger = logging.getLogger("Monitor_DB")
        self.base = commonBase
        self.ormList = []
        self.translator = Translator()

    def init_all_tables(self):
        self.base.metadata.create_all(bind=self.engine)

    def make_session(self):
        self.session = sessionmaker(bind=self.engine)()

    def add_detector_data(self, dataFilepath, timestamp):
        self.ormList.append(self.translator.from_txt_to_detector_ORM(dataFilepath, timestamp))

    def add_lowres_image(self, filepath, timestamp):
        self.ormList.append(self.translator.from_image_to_lowres_ORM(filepath, timestamp))

    def add_highres_image(self, filepath, timestamp):
        self.ormList.append(self.translator.from_image_to_highres_ORM(filepath, timestamp))

    def clear_table(self, tableName):
        table = Table("{}".format(tableName))
        try:
            self.session.delete(table)
            self.session.commit()
        except Exception:
            self.session.rollback()

    def clear_orm_list(self):
        self.ormList = []

    def commit_data(self):
        try:
            self.make_session()
            for orm in self.ormList:
                for data in orm:
                    self.session.add(data)
            self.session.commit()
            self.clear_orm_list()
        except Exception as E:
            self.clear_orm_list()
            self.logger.exception(E)
            self.logger.exception('Lost connection to database')


if __name__ == '__main__':
    dbc = DatabaseClient(config=localhost_database_config)
    dbc.init_all_tables()
    # dbc.add_lowres_image(["highres.jpg", "lowres.jpg"], ["1900-06-06 12:00:00", "1900-06-06 12:00:00"])
    # dbc.commit_data()
