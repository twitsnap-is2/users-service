from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.exc import NoResultFound, SQLAlchemyError, IntegrityError
from sqlalchemy.orm import sessionmaker
from loguru import logger
from business_logic.users.users_model import Users, UserInfo
from business_logic.users.users_schemas import UserAccountBase, UserCreationResponse, UserCompleteCreation,UserInfoResponse
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
        user_model_instance = Users(username=user.username, name=user.name, email=user.email, profilePic=None, createdat=timestamp)
        # userinfo_model_instance = UserInfo(birthdate=user.birthdate, location=user.location)
        # user_model_instance.userinfo = userinfo_model_instance
        with Session(self.engine) as session:
            try: 
                session.add(user_model_instance)
                session.commit()
                logger.info("User inserted successfully")
                new_user = UserCreationResponse(id=user_model_instance.id, username=user.username, email=user.email, name=user.name, created_at=timestamp)
            except IntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                session.rollback()
                raise e
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                session.rollback()
                raise e
            finally:
                session.close()

        return new_user
    
    def get_user_by_id(self, user_id: str):
        with Session(self.engine) as session:
            try:
                statement = select(Users).where(Users.id == UUID(user_id))
                user = session.scalars(statement).one()
                user_creation_response = UserInfoResponse(
                    id=user.id,
                    username=user.username,
                    name=user.name,
                    email=user.email,
                    created_at=user.createdat.isoformat(),
                    profilePic=user.profilePic,
                    birthdate=user.userinfo.birthdate if user.userinfo else None,
                    locationLat=user.userinfo.locationLat  if user.userinfo else None,
                    locationLong=user.userinfo.locationLong  if user.userinfo else None,
                    interests=user.userinfo.interests if user.userinfo else None
                )
                logger.info("User retrieved successfully")  
                return user_creation_response
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")


    def get_email_by_username(self, username: str):
        with Session(self.engine) as session:
            try:
                statement = select(Users.email).where(Users.username == username)
                email = session.scalars(statement).one_or_none()
                if email:
                    logger.info("Email retrieved successfully in database")
                    return email
                else: 
                    logger.error("Email not found")
                    return None
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")

    def check_email_exists(self, email: str):
        with Session(self.engine) as session:
            try:
                statement = select(Users.email).where(Users.email == email)
                email = session.scalars(statement).one_or_none()
                if email:
                    logger.info("Email retrieved successfully in database")
                    return {"exists": True}
                else: 
                    logger.error("Email not found")
                    return {"exists": False}
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")


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
                        created_at=user.createdat.isoformat(),
                        profilePic=user.profilePic
                    )
                    users.append(user_creation_response)
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
            finally:
                session.close()
        logger.info(f"Users RETURNED: {users}")
        return users

    def update_user_id(self, user_id: str, data: UserCompleteCreation):
        with Session(self.engine) as session:
            try:
                statement = select(Users).where(Users.id == UUID(user_id))
                user = session.scalars(statement).one()
                if not user:
                    logger.error("Invalid user id")
                    return None
                user.id = data.supabase_id
                logger.info(f"User id: {user.id}, profilePic: {data.profilePic}")
                user.profilePic = data.profilePic
                user.userinfo = UserInfo(birthdate=data.birthdate, locationLat=data.locationLat, locationLong=data.locationLong)
                session.commit()
                logger.info("User updated successfully")
                return user
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                session.rollback()
                raise e

    def get_user_authors_info(self, user_id: str, authors: list[str]):
        authors_info = []
        with Session(self.engine) as session:
            try:
                statement = select(Users).where(Users.username.in_(authors))
                authors = session.scalars(statement).all()
                for author in authors:
                    author_info = UserCreationResponse(
                        id=author.id,
                        username=author.username,
                        name=author.name,
                        email=author.email,
                        created_at=author.createdat.isoformat(),
                        profilePic=author.profilePic,
                    )
                    authors_info.append(author_info)
                logger.info("Authors info retrieved successfully")
                return authors_info
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy Error: {e}")

    def get_usernames_starting_with(self, string: str):
        users = []
        with Session(self.engine) as session:
            try:
                statement = select(Users).where(Users.username.ilike(string))
                user_objects = session.scalars(statement).all()
                for user in user_objects:
                    user_creation_response = UserCreationResponse(
                        id=user.id,
                        username=user.username,
                        name=user.name,
                        email=user.email,
                        created_at=user.createdat.isoformat(),
                        profilePic=user.profilePic
                    )
                    users.append(user_creation_response)
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
            
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

    