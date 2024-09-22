from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from loguru import logger
from utils.engine import get_engine
from bussiness_logic import models

class Database:
    def __init__(self, engine_url):
        self.engine = create_engine(engine_url)
        self.metadata = MetaData()
        self.table = self.create_table()

    def create_table(self):
        table = Table(
            "messages",
            self.metadata,
            Column("id", String, primary_key=True),
            Column("message", String),
        )
        try:
            with self.engine.connect() as connection:
                table.drop(connection, checkfirst=True)  
                self.metadata.create_all(connection) 
                logger.info("Table created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating table: {e}")
        return table

    def get_echomsg(self, echomsg_id: int):
        return self.get_session().query(models.EchoMsg).filter(models.EchoMsg.id == echomsg_id).first()

    def create_echomsg(echomsg: schemas.EchoMsgCreate, echomsg_id: int):
        db_echomsg = models.EchoMsg(msg=echomsg.msg, id=echomsg_id)
        session = self.get_session()
        session.add(db_echomsg)
        session.commit()
        session.refresh(db_echomsg)
        return db_echomsg

    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()

    def clear_table(self):

        session = self.get_session()
        try:
            session.execute(self.table.delete())
            session.commit()
            logger.info("Table cleared successfully.")
        except Exception as e:
            logger.error(f"Error clearing table: {e}")
            session.rollback()
        finally:
            session.close()

    def drop_table(self):
        """
        Drop the table from the database.
        """
        try:
            with self.engine.connect() as connection:
                self.table.drop(connection)
                logger.info("Table dropped successfully.")
        except Exception as e:
            logger.error(f"Error dropping table: {e}")