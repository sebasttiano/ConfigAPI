"""DB basics"""

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from settings import db_url


engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
