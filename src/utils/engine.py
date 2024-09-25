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

def get_test_engine() -> Optional[create_engine]:
    test_user = os.getenv('TEST_POSTGRES_USER')
    test_password = os.getenv('TEST_POSTGRES_PASSWORD')
    test_host = os.getenv('TEST_POSTGRES_HOST')
    test_port = os.getenv('TEST_POSTGRES_PORT')
    test_db = os.getenv('TEST_POSTGRES_DB')
    test_database_url = f"postgresql://{test_user}:{test_password}@{test_host}:{test_port}/{test_db}"

    logger.info("Connecting Test Database via URL")

    return create_engine(test_database_url, echo=True)

