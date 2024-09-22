from typing import List
from typing import Optional
from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    id: Mapped[str] = Column(primary_key=True)
    username: Mapped[str] = Column(String, unique=True)
    mail: Mapped[str] = Column(String, unique=True)
    password: Mapped[str] = Column(String)
    # createdAt 
    # interests

