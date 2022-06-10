import logging

from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()

class Cars(Base):
    """Cars table: more than 0.25 million us. Contains general info about the cars and their cluster
    assignments.
    """
    __tablename__ = 'cars'

    car_id = Column(String(100), primary_key=True)
    genmodel_id = Column(String(100))
    maker = Column(String(100))
    genmodel = Column(String(100))
    year = Column(Integer)
    bodytype = Column(String(100))
    gearbox = Column(String(100))
    engin_size = Column(Float)
    fuel_type = Column(String(100))
    price = Column(Float)
    seat_num = Column(Float)
    door_num = Column(Float)
    cluster = Column(Integer)

    def __repr__(self):
        return f'Maker:{self.maker}, Model:{self.genmodel}, Year:{self.year}, Cluster:{self.cluster}.'


def create_db(engine_string: str) -> None:
    """Connect to an SQL engine through engine string and create
    a data base.

    Args:
        engine_string (str): The SQL Engine Path.
    """
    # Set up sqlite connection
    engine = create_engine(engine_string)

    # Create the tracks table
    Base.metadata.create_all(engine)
    logger.info('Database created!')
