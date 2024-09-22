from typing import Optional
from sqlalchemy import create_engine
from loguru import logger
import os

def get_engine() -> Optional[create_engine]:
    return create_engine(
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}",
        echo=True,
    )
