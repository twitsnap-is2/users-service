from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import sessionmaker
from loguru import logger
from utils.engine import get_engine
from business_logic.users.users_model import Users
from business_logic.users.users_schemas import UserAccountCreate
from sqlalchemy.orm import Session
from sqlalchemy import select
from business_logic.users.users_model import Base

class Database:
    def __init__(self, engine):
        self.engine = engine
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

            table_exists = connection.dialect.has_table(connection, "users")
            if table_exists:
                logger.info("Table exists")
            else:
                logger.info("Table does not exist")


    def insert_user(self, user: UserAccountCreate):
        user_model_instance = Users(id=user.id, username=user.username, mail=user.mail, password=user.password)
        with Session(self.engine) as session:
            try: 
                session.add(user_model_instance)
                session.commit()
                logger.info("User inserted successfully")
            
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

        return True


    def get_users(self):
        users = []
        with Session(self.engine) as session:
            try:
                statement = select(Users)
                users = session.scalars(statement).all()
                logger.info("Users retrieved successfully")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
            finally:
                session.close()

        return users
        


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