from sqlalchemy import MetaData, Table, Column, String, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging as logger
from sqlalchemy.orm import Session
from database.db import Database
from business_logic.users.users_schemas import UserAccountBase
from uuid import uuid4

class UserAccountService:

    def __init__(self, engine):
        self.database = Database(engine)

    def insert_useraccount(self, user: UserAccountBase):
        return self.database.insert_user(user)

    def get_useraccounts(self):
        return self.database.get_users()
        


