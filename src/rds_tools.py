import logging
from operator import index
import os
import typing

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

Base = declarative_base()

class Basic(Base):
    """Basic table: car attributes such as model name, model ID and brand name."""

    __tablename__ = "basics"
    
    # create columns
    genmodel_id = Column(String(100), primary_key=True, index=True)
    genmodel = Column(String(100), nullable=False)
    automaker_id = Column(Integer)
    automaker = Column(String(100))

    def __repr__(self):
        return f'<Basic: "{self.genmodel}" - {self.automaker}>'


class Image(Base):
    """Image table: car images attributes like name."""
    __tablename__ = "images"

    image_id = Column(String(100), primary_key=True)
    image_name = Column(String(100), nullable=False)

    genmodel_id = Column(String(100), ForeignKey("basics.genmodel_id"))

    basic = relationship("Basic", back_populates="images")

    def __repr__(self):
        return f'<Image: "{self.image_name}" - {self.basic.genmodel}>'


class Trim(Base):
    """Trim table: trim attributes like the selling price (trim level), engine type and engine size."""
    __tablename__ = "trims"

    id = Column(Integer, primary_key=True)
    trim = Column(String(200))
    year = Column(Integer)
    price = Column(Integer)
    gas_emission = Column(Integer)
    fuel_type = Column(String(100))
    engine_size = Column(Integer)

    genmodel_id = Column(String(100), ForeignKey("basics.genmodel_id"))

    basic = relationship("Basic", back_populates="trims")

    def __repr__(self):
        return f'<Image: "{self.trim}" - {self.basic.genmodel}>'


class Ad(Base):
    """Ad table: more than 0.25 million used car advertisements. Contains some info about cars"""
    __tablename__ = "ads"

    adv_id = Column(String(100), primary_key=True)
    reg_year = Column(Integer)
    bodytype = Column(String(100))
    gearbox = Column(String(100))
    engin_size = Column(String(100))
    fuel_type = Column(String(100))
    seat_num = Column(Integer)
    door_num = Column(Integer)

    genmodel_id = Column(String(100), ForeignKey("basics.genmodel_id"))

    basic = relationship("Basic", back_populates="ads")

    def __repr__(self):
        return f'<Image: "{self.adv_id}" - {self.basic.genmodel}>'

class Price(Base):
    """Price table: entry-level (i.e. the cheapest trim price) new car prices across years."""
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    entry_price = Column(Integer)

    genmodel_id = Column(String(100), ForeignKey("basics.genmodel_id"))

    basic = relationship("Basic", back_populates="prices")

    def __repr__(self):
        return f'<Image: "{self.entry_price}" - {self.basic.genmodel}>'

def create_db(engine_string: str):

    # Set up sqlite connection
    engine = create_engine(engine_string)

    # Set up looging config
    logger = logging.getLogger(__file__)

    # Create a db session
    # Session = sessionmaker(bind=engine)

    # Create the tracks table
    Base.metadata.create_all(engine)
    logger.info("Database created!")
