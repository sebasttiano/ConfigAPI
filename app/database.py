"""DB basics"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import db_url


engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
