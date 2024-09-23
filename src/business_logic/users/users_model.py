from typing import List
from typing import Optional
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, unique=True)
    username = Column(String, unique=True)
    mail = Column(String, unique=True)
    password = Column(String)
    # createdAt 
    # interests

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, mail={self.mail!r})"
