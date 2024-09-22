from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

class EchoMsg(Base):
    __tablename__ = "echomsg"

    id: Mapped[int] = Column(primary_key=True)
    msg: Mapped[str] = Column()

