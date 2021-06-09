import gzip
import json
import logging
import sys
import requests


import boto3
import botocore.exceptions

logger = logging.getLogger(__name__)


def download(url, gzip_filepath, unzipped_filepath):
    """
    Downloads the data necessary for the app and saves it locally.
    Args:
        url: obj:`String` webpage where the data is located
        gzip_filepath: obj:`String` filepath to where the downloaded data should be saved locally.
        unzipped_filepath: obj:`String` filepath to where the unzipped data will be saved.
    Returns:
        None
    """

    # Download the raw data from given url
    try:
        logger.debug("Beginning download from %s", url)
        r = requests.get(url)
        with open(gzip_filepath, "wb") as f:
            f.write(r.content)
        logger.info("Data has been successfully downloaded and saved to %s", gzip_filepath)

    except requests.exceptions.ConnectTimeout as e:
        logger.error('%s, The request timed out while trying to connect to the remote server', e)
        sys.exit(3)

    except requests.exceptions.InvalidURL as e:
        logger.error('%s, The specified URL was invalid', e)
        sys.exit(3)

    except requests.exceptions.ConnectionError as e:
        logger.error('%s, There was a connection error, check your internet connection and try again', e)
        sys.exit(3)

    except Exception as e:
        logger.error(e)
        sys.exit(3)

    # Unzip the downloaded file and save the unzipped file
    try:
        dict_list = []
        logger.debug('Parsing gzip file with generator function')
        for line in parse(gzip_filepath):
            dict_list.append(line)
        logger.debug("%s has %d rows", unzipped_filepath, len(dict_list))

        if len(dict_list) == 0:
            logger.warning("Parsed data contains 0 rows")

        with open(unzipped_filepath, 'w') as f:
            json.dump(dict_list, f)
        logger.info("Gzip file has been unzipped and saved to %s", unzipped_filepath)

    except json.JSONDecodeError as e:
        logger.error("%s, could not parse json file. Make sure the file is in the correct format", e)

    except Exception as e:
        logger.error(e)
        sys.exit(3)


def download_s3(unzipped_filepath, bucket_name, bucket_filepath):
    """
    Downloads data file from a S3 bucket.
    Args:
        unzipped_filepath: obj:`String` filepath to where the data is saved locally. Should be in the format of x.json
        bucket_name: obj:`String` name of the S3 bucket located on AWS
        bucket_filepath: obj:`String` where the data is located on the S3 bucket. Should be in the format of x.json

    Returns:
        None
    """
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)

    try:
        bucket.download_file(bucket_filepath, unzipped_filepath)
        logger.info('Data downloaded from %s to %s', bucket_filepath, unzipped_filepath)

    except botocore.exceptions.NoCredentialsError as e:
        logger.error('%s, check to make sure your aws credentials are correctly sourced', e)
        sys.exit(3)

    except botocore.exceptions.ConnectionError as e:
        logger.error('%s, Could not connect to the s3 bucket. Check your internet connection', e)
        sys.exit(3)

    except botocore.exceptions.DataNotFoundError as e:
        logger.error('%s, could not find data file on S3. Check to make sure the path is correct', e)
        sys.exit(3)

    except Exception as e:
        logger.error(e)
        sys.exit(3)


def parse(path):
    """Generator function that yields one unzipped line of the gzip file"""
    gzip_file = gzip.open(path, 'r')
    for line in gzip_file:
        yield eval(line)


def upload(unzipped_filepath, bucket_name, bucket_filepath):
    """
    Uploads data to a S3 bucket. This function does not return anything, it connects to the specified S3 bucket
    and uploads the file located at the data path variable and stores it at the bucket_path variable.
    Args:
        unzipped_filepath: obj:`String` filepath to where the data is stored locally. Should be in the format of x.json
        bucket_name: obj:`String` name of the S3 bucket located on AWS
        bucket_filepath: obj:`String` where the data should be saved on the S3 bucket. Should be in the format of x.json

    Returns:
        None
    """

    # Upload Data to S3
    try:
        logger.debug("Beginning data upload to %s", bucket_name)
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket_name)
        bucket.upload_file(unzipped_filepath, bucket_filepath)
        logger.info("Data has been successfully uploaded to S3 and can be found at %s", bucket_filepath)

    except botocore.exceptions.NoCredentialsError as e:
        logger.error('%s, check to make sure your aws credentials are correctly sourced', e)
        sys.exit(3)

    except botocore.exceptions.ConnectionError as e:
        logger.error('%s, Could not connect to the s3 bucket. Check your internet connection', e)
        sys.exit(3)

    except Exception as e:
        logger.error(e)
        sys.exit(3)
