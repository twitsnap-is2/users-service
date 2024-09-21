from typing import Optional
from sqlalchemy import create_engine
from loguru import logger
import os

def get_engine() -> Optional[create_engine]:
    return create_engine(os.getenv("DATABASE_URL"),
                         echo=True,
                         )

