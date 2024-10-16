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

    internal_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    # supabase_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    username = Column(String, unique=True)
    name = Column(String)
    email = Column(String, unique=True)
    profilePic = Column(String)
    createdat = Column(DateTime, default=datetime.datetime.utcnow)

    userinfo = relationship("UserInfo", back_populates="user", uselist=False)

     # Representa a los usuarios que siguen al usuario
    followers = relationship("Followers", foreign_keys="[Followers.followed_id]", back_populates="followed", cascade="all, delete-orphan")

    # Representa a los usuarios que el usuario sigue
    following = relationship("Followers", foreign_keys="[Followers.follower_id]", back_populates="follower", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, email={self.email!r})"

class UserInfo(Base):
    __tablename__ = "userinfo"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True, nullable=False)
    birthdate = Column(String)
    locationLat = Column(String)
    locationLong = Column(String)
    interests = Column(String)

    user = relationship("Users", back_populates="userinfo", uselist=False)

    def __repr__(self) -> str:
        return f"UserInfo(id={self.id!r}, user_id={self.user_id!r}, birthdate={self.birthdate!r}, locationLat={self.locationLat!r}, locationLong={self.locationLong!r}, interests={self.interests!r})" 

class Followers(Base):
    __tablename__ = "followers"
    
    follower_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True, nullable=False) # Usuario que sigue
    followed_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True, nullable=False) # Usuario que es seguido
    followed_at = Column(DateTime, default=datetime.datetime.now(tz=datetime.timezone.utc))

    follower = relationship("Users", foreign_keys=[follower_id], back_populates="following")
    followed = relationship("Users", foreign_keys=[followed_id], back_populates="followers")

    def __repr__(self) -> str:
        return f"Followers(follower_id={self.follower_id!r}, followed_id={self.followed_id!r}, followed_at={self.followed_at!r})"