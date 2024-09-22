from sqlalchemy import MetaData, Table, Column, String, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from utils import get_engine
import logging as logger
from sqlalchemy.orm import Session
from bussiness_logic.database import Database

class Services:

    def __init__(self, engine_url):
        self.database = Database(engine_url)

    def clear_table(self):

        session = self.database.get_session()
        try:
            session.execute(self.database.table.delete())
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
            with self.database.engine.connect() as connection:
                self.database.table.drop(connection)
                logger.info("Table dropped successfully.")
        except Exception as e:
            logger.error(f"Error dropping table: {e}")