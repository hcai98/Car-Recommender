
import argparse
from src.rds_tools import create_db


if __name__ == "__main__":
    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(
        description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for creating a database
    sp_create = subparsers.add_parser("create_db",
                                      description="Create database")
    sp_create.add_argument("--engine_string",
                           help="SQLAlchemy connection URI for database")

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == 'create_db':
        create_db(args.engine_string)
    elif sp_used == 'ingest':
        pass;
    else:
        parser.print_help()
