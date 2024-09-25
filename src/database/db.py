from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import sessionmaker
from loguru import logger
from utils.engine import get_engine
from business_logic.users.users_model import Users, UserInfo
from business_logic.users.users_schemas import UserAccountBase, UserCreationResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from business_logic.users.users_model import Base
from datetime import datetime, timedelta, timezone
from uuid import UUID

class Database:
    def __init__(self, engine):
        self.engine = engine
        self.users_table = Users.__table__
        self.userinfo_table = UserInfo.__table__
        self.create_table()

    def create_table(self):
        with self.engine.connect() as connection:
            try:
                Base.metadata.create_all(bind=connection) 
                logger.info("Table created successfully")
                connection.commit()
            except SQLAlchemyError as e:
                logger.error(f"Error creating table: {e}")
                connection.rollback()

            table_user_exists = connection.dialect.has_table(connection, "users") 
            if table_user_exists:
                logger.info("Table 'users' exists")
            else:
                logger.info("Table does not exist")

            if connection.dialect.has_table(connection, "userinfo"):
                logger.info("Table 'userinfo' exists")
            else:
                logger.info("Table 'userinfo' does not exist")

    def insert_user(self, user: UserAccountBase):
        local_timezone = timezone(timedelta(hours=-3))
        timestamp = datetime.now(local_timezone).isoformat()
        user_model_instance = Users(username=user.username, name=user.name, email=user.email, profilepic=None, createdat=timestamp)
        userinfo_model_instance = UserInfo(birthdate=user.birthdate, location=user.location)
        user_model_instance.userinfo = userinfo_model_instance
        with Session(self.engine) as session:
            try: 
                session.add(user_model_instance)
                session.commit()
                logger.info("User inserted successfully")
                new_user = UserCreationResponse(id=user_model_instance.id, username=user.username, email=user.email, name=user.name, birthdate=user.birthdate, created_at=timestamp)
            except IntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                session.rollback()
                return False
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                session.rollback()
                return False
            finally:
                session.close()

        return new_user
    
    def get_user_by_id(self, user_id: str):
        with Session(self.engine) as session:
            try:
                statement = select(Users).where(Users.id == UUID(user_id))
                user = session.scalars(statement).one()
                user_creation_response = UserCreationResponse(
                    id=user.id,
                    username=user.username,
                    name=user.name,
                    email=user.email,
                    birthdate=user.userinfo.birthdate,
                    created_at=user.createdat.isoformat(),
                    profilepic=user.profilepic
                )
                logger.info("User retrieved successfully")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")

        return user_creation_response

    def get_users(self):
        users = []
        with Session(self.engine) as session:
            try:
                statement = select(Users)
                user_objects = session.scalars(statement).all()
                logger.info("Users retrieved successfully")
                for user in user_objects:
                    user_creation_response = UserCreationResponse(
                        id=user.id,
                        username=user.username,
                        name=user.name,
                        email=user.email,
                        birthdate=user.userinfo.birthdate,
                        created_at=user.createdat.isoformat(),
                        profilepic=user.profilepic
                    )
                users.append(user_creation_response)
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
            finally:
                session.close()
        logger.info(f"Users RETURNED: {users}")
        return users

    def clear_table(self):

        with Session(self.engine) as session:
            try:
                session.execute(self.userinfo_table.delete())
                session.execute(self.users_table.delete())
                session.commit()
                logger.info("Tables cleared successfully.")
            except Exception as e:
                logger.error(f"Error clearing tables: {e}")
                session.rollback()
            finally:
                session.close()

    def drop_table(self):
        """
        Drop the table from the database.
        """
        try:
            with self.engine.connect() as connection:
                self.userinfo_table.drop(connection)
                self.users_table.drop(connection)
                logger.info("Tables dropped successfully.")
        except Exception as e:
            logger.error(f"Error dropping table: {e}")