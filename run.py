import argparse

from src.get_data import download, upload
from src.createTable import createTable
from config.flaskconfig import SQLALCHEMY_DATABASE_URI

if __name__ == '__main__':

    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create database")
    sb_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # Sub-parser for ingesting new data
    sp_data = subparsers.add_parser("get_data", description="Downloads or Uploads data from the internet or S3")
    sp_data.add_argument("--upload", default=True, help="")
    sp_data.add_argument("--url", default="http://deepx.ucsd.edu/public/jmcauley/steam/australian_users_items.json.gz", help="url to acquire data from")
    sp_data.add_argument("--gzip_file_path", default="data/australian_users_items.json.gz", help="Local File path to save data file")
    sp_data.add_argument("--bucket_name", default="2021-msia423-faulkner-michael", help="s3 bucket name")
    sp_data.add_argument("--bucket_path", default='data.json.gz', help="SQLAlchemy connection URI for database")

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == 'create_db':
        createTable(args.engine_string)
    elif sp_used == 'get_data':
        download(args.url, args.gzip_file_path)
        if args.upload:
            upload(args.gzip_file_path, args.bucket_name, args.bucket_path)
    else:
        parser.print_help()
