from sqlalchemy import MetaData, Table, Column, String, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging as logger
from sqlalchemy.orm import Session
from database.db import Database
from business_logic.users.users_schemas import UserAccountBase, UserCompleteCreation
from uuid import uuid4

class UserAccountService:

    def __init__(self, engine):
        self.database = Database(engine)

    def insert_useraccount(self, user: UserAccountBase):
        if not user.username:
            raise ValueError("Username is required")
        return self.database.insert_user(user)

    def get_useraccounts(self):
        return self.database.get_users()

    def get_useraccount(self, user_id: str):
        return self.database.get_user_by_id(user_id)
    
    def get_user_authors_info(self, user_id: str, authors: list[str]):
        return self.database.get_user_authors_info(user_id, authors)

    def get_email_by_username(self, username: str):
        return self.database.get_email_by_username(username)
    
    def check_email_exists(self, email: str):
        return self.database.check_email_exists(email)

    def update_useraccount(self, user_id: str, data: UserCompleteCreation):
        return self.database.update_user_id(user_id, data)
    
