from typing import Optional
from sqlalchemy import create_engine
from loguru import logger
import os
from dotenv import load_dotenv

def get_engine() -> Optional[create_engine]:
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_HOST')
    port = os.getenv('POSTGRES_PORT')
    db = os.getenv('POSTGRES_DB')
    database_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"

    logger.info("Connecting Database via URL")
    
    return create_engine(database_url, echo=True)
