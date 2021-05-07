import argparse
import logging.config

from config.flaskconfig import SQLALCHEMY_DATABASE_URI
from src.create_db import create_db
from src.get_data import download, upload

logging.config.fileConfig("config/logging/local.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    # Add parsers for downloading/uploading data to S3 and creating tht databse
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create database")
    sb_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # Sub-parser for downloading/uploading data to S3
    sp_data = subparsers.add_parser("get_data", description="Downloads or Uploads data from the internet or S3")
    sp_data.add_argument("--url", default="http://deepx.ucsd.edu/public/jmcauley/steam/australian_users_items.json.gz",
                         help="url to acquire data from")
    sp_data.add_argument("--gzip_file_path", default="data/raw/australian_users_items.json.gz",
                         help="Local File path to save data file")
    sp_data.add_argument("--unzipped_file_path", default="data/raw/australian_users_items.json",
                         help="Local file path for unzipped data file")
    sp_data.add_argument("--bucket_name", default="2021-msia423-faulkner-michael", help="s3 bucket name")
    sp_data.add_argument("--bucket_file_path", default='raw/data.json', help="SQLAlchemy connection URI for database")

    args = parser.parse_args()
    sp_used = args.subparser_name

    logging.info("Running function %s", sp_used)

    if sp_used == 'create_db':
        create_db(args.engine_string)
    elif sp_used == 'get_data':
        download(args.url, args.gzip_file_path, args.unzipped_file_path)
        upload(args.unzipped_file_path, args.bucket_name, args.bucket_file_path)
    else:
        parser.print_help()
