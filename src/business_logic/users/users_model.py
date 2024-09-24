from typing import List
from typing import Optional
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, ForeignKey, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime


class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True)
    name = Column(String)
    email = Column(String, unique=True)
    profilePic = Column(String)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)

    userinfo = relationship("UserInfo", back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, email={self.mail!r})"

class UserInfo(Base):
    __tablename__ = "userinfo"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    birthdate = Column(String)
    location = Column(String)
    interests = Column(String)

    user = relationship("Users", back_populates="userinfo")

    def __repr__(self) -> str:
        return f"UserInfo(id={self.id!r}, user_id={self.user_id!r}, birthdate={self.birthdate!r}, location={self.location!r}, interests={self.interests!r})"