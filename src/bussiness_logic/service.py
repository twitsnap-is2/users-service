from sqlalchemy import MetaData, Table, Column, String, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from utils import get_engine
import logging as logger
from sqlalchemy.orm import Session
from bussiness_logic.database import Database

class Services:

    def __init__(self, engine_url):
        self.database = Database(engine_url)


    def insert_echomsg(self, msg: str):
        echomsg_id = 1
        try:
            return self.database.create_echomsg(msg, echomsg_id)
        except IntegrityError as e:
            logger.error(f"Error inserting message: {e}")
            raise e

    def get_echomsg(self, echomsg_id: int):
        return self.database.get_echomsg(echomsg_id)


