from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from loguru import logger
from utils.engine import get_engine

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

    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()