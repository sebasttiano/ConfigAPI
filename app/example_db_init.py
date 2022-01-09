import csv
import os
from sqlalchemy.exc import OperationalError, IntegrityError
from models import Devices, Base
from database import SessionLocal, engine
from settings import PROJECT_DIR
from decorators import CheckExceptions


@CheckExceptions((OperationalError, IntegrityError))
def init_db(populate_from_csv: bool = True) -> None:
    """Generates tables and populates with example data"""
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    if populate_from_csv:
        with open(f"{os.path.split(PROJECT_DIR)[0]}/example_data.csv", "r") as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                db_record = Devices(
                    name=row["name"],
                    type=row["type"],
                    role=row["role"],
                    vendor=row["vendor"],
                    model=row["model"],
                    ip=row["ip"],
                    location=row["location"],
                    description=row["description"]
                )
                db.add(db_record)
            db.commit()

    db.close()