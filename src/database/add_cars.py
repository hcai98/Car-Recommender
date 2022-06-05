"""Creates, ingests data into, and enables querying of a table of
 songs for the PennyLane app to query from and display results to the user."""
# mypy: plugins = sqlmypy, plugins = flasksqlamypy
import argparse
import logging.config
import sqlite3
import typing

import flask
import sqlalchemy
import sqlalchemy.orm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd

from src.utils import io
from src.database.create_db import Cars

logger = logging.getLogger(__name__)

Base: typing.Any = declarative_base()


class CarManager:
    """Creates a SQLAlchemy connection to the tracks table.

    Args:
        app (:obj:`flask.app.Flask`): Flask app object for when connecting from
            within a Flask app. Optional.
        engine_string (str): SQLAlchemy engine string specifying which database
            to write to. Follows the format
    """

    def __init__(self, app: typing.Optional[flask.app.Flask] = None,
                 engine_string: typing.Optional[str] = None):
        if app:
            self.database = SQLAlchemy(app)
            self.session = self.database.session
        elif engine_string:
            engine = sqlalchemy.create_engine(engine_string)
            session_maker = sqlalchemy.orm.sessionmaker(bind=engine)
            self.session = session_maker()
        else:
            raise ValueError(
                "Need either an engine string or a Flask app to initialize")

    def close(self) -> None:
        """Closes SQLAlchemy session

        Returns: None

        """
        self.session.close()

    def add_car_df(self, input_path: str) -> None:
        """Add the car data into the data base.

        Args:
            input_path (str): Path to the car data.

        Returns:
            None
        """
        # establish session
        session = self.session
        logger.debug("Session retrieved.")

        # load data frame
        cars = io.read_pandas(input_path=input_path)
        logger.info("Car data (with assignment) loaded.")

        # every element corresponds to a row in the data frame.
        car_dict_list = cars.to_dict(orient='records')
        logger.debug("Transformed df into list. Length: %s",
                     len(car_dict_list))

        # convert dict to records and put all records in a list
        car_record_list = []
        for car_dict in car_dict_list:
            car_record_list.append(Cars(**car_dict))
        logger.debug("Collected all records into list. Length: %s",
                     len(car_record_list))

        # add all records to data base
        try:
            logger.info("Adding record list to database...")
            session.add_all(car_record_list)
            session.commit()
            logger.info("Data loaded into database.")
        except sqlalchemy.exc.OperationalError:
            logger.error("Operational error occurred. "
                         "Check your connection to the database")
        except sqlalchemy.exc.IntegrityError:
            logger.error("The database already contains the records you are trying to insert. "
                         "Please truncate the table before attempting again.")


def add_car_df(input_path: str, engine_string: str) -> None:
    """Add a car table to the data base.

    Args:
        input_path (str): Path to the car table.
        engine_string (str): Engine string of the sql server.
    """
    logger.info("Adding car data frame to the database...")

    # create a car manager instance
    car_manager = CarManager(engine_string=engine_string)
    logger.debug('Car manager created')

    try:
        # use manager to add data to data base
        car_manager.add_car_df(input_path)
        logger.info('Data frame added to database.')
    except sqlite3.OperationalError as err_oe:
        logger.error(
            "Error page returned. Not able to add song to local sqlite "
            "database: %s. Is it the right path? Error: %s ",
            engine_string, err_oe)
    except sqlalchemy.exc.OperationalError as err_oe:
        logger.error(
            "Error page returned. Not able to add song to MySQL database.  "
            "Please check engine string and VPN. Error: %s ", err_oe)

    car_manager.close()
