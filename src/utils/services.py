from sqlalchemy import MetaData, Table, Column, String, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from utils import get_engine
import logging as logger
from sqlalchemy.orm import Session

class Services:
    """
    Class that sores data in a db through sqlalchemy
    """

    def __init__(self):
        self.engine = get_engine()
        self.create_table()
        logger.getLogger("sqlalchemy.engine").setLevel(logger.DEBUG)

    def create_table(self):
        """
        Creates a table in the db
        """
        metadata = MetaData()
        # self.<nombre de la tabla que quiero>
        self.table = Table(
            "messages",
            metadata,
            Column("id", String, primary_key=True),
            Column("message", String),
        )
        try:
            with self.engine.connect() as connection:
                self.table.drop(connection, checkfirst=True)
                metadata.create_all(connection)
                logger.info("Table created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating table: {e}")

    def clear_table(self):
        """
        Clear the table from the database.
        """
        try:
            with Session(self.engine) as session:
                session.execute(self.snapmsgs.delete())
                session.commit()
                logger.info("Table cleared successfully.")
        except Exception as e:
            logger.error(f"Error clearing table: {e}")
            session.rollback()

    def drop_table(self):
        """
        Drop the table from the database.
        """
        try:
            with self.engine.connect() as connection:
                self.snapmsgs.drop(connection)
                logger.info("Table dropped successfully.")
        except Exception as e:
            logger.error(f"Error dropping table: {e}")