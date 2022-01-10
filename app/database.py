"""DB basics"""

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from settings import DB_URL


engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
