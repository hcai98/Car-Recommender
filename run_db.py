import argparse
import logging.config

from src.database.create_db import create_db
from src.database.add_cars import add_car_df
from config.flaskconfig import SQLALCHEMY_DATABASE_URI
from config import dbconfig

# configure logger
logging.config.fileConfig(dbconfig.LOGGING_CONFIG)
logger = logging.getLogger()


if __name__ == "__main__":
    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(
        description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for creating a database
    sp_create = subparsers.add_parser("create_db",
                                      description="Create database")
    sp_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # Sub-parser for ingesting new data
    sp_ingest = subparsers.add_parser("ingest",
                                      description="Add data to database")
    sp_ingest.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")
    sp_ingest.add_argument("--input", default=None,
                           help="Path of the data frame to be added")

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == 'create_db':
        create_db(args.engine_string)
    elif sp_used == 'ingest':
        add_car_df(input_path=args.input, engine_string=args.engine_string)
    else:
        parser.print_help()
