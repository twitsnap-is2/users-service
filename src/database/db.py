from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import sessionmaker
from loguru import logger
from utils.engine import get_engine
from business_logic.users.users_model import Users
from business_logic.users.users_schemas import UserAccountCreate


class Database:
    def __init__(self, engine):
        self.engine = engine
        self.metadata = MetaData()
        self.users = self.create_table()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_table(self):
        self.users = Table(
            "users",
            self.metadata,
            Column("id", String, primary_key=True),
            Column("username", String),
            Column("mail", String),
            Column("password", String),
            schema="public"
        )
        try:
            with self.engine.connect() as connection:
                self.metadata.create_all(connection) 
                logger.info("Table created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating table: {e}")
        return self.users

    def insert_user(self, user: UserAccountCreate):
        session = self.SessionLocal()
        try:
            query = self.users.insert().values(
                id=user.id, username=user.username, mail=user.mail, password=user.password
            )
            session.execute(query)
            session.commit()
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