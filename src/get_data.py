import gzip
import logging.config

import requests
import shutil
import sys

import boto3
import botocore.exceptions

logging.config.fileConfig("config/logging/local.conf")
logger = logging.getLogger(__name__)


def download(url, gzip_save_path, unzipped_file_path):
    """ Downloads the data necessary for the app and saves it locally. This function does not return anything, instead
        it downloads the steam/user data from the given url and saves it in the docker data folder.
    Args:
        url:obj:`String` webpage where the data is located
        gzip_save_path:obj:`String` filepath to where the downloaded data should be saved locally. Should be in the \
        format of x.gz.
        unzipped_file_path:obj:`String` filepath to where the unzipped data will be saved. Should be in the format of \
        x.json

    Returns:
        None
    """

    # Download the raw data from given url
    try:
        logger.info("Beginning download from %s", url)
        r = requests.get(url)
        with open(gzip_save_path, "wb") as f:
            f.write(r.content)
        logger.info("Data has been successfully downloaded and saved to %s", gzip_save_path)

    except Exception as e:
        logger.error(e)
        sys.exit(3)

    # Unzip the downloaded file and save the unzipped file
    try:
        logger.info("Unzipping gzip file")
        with gzip.open(gzip_save_path, 'rb') as f_in:
            with open(unzipped_file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        logger.info("Gzip file has been unzipped and saved to %s", unzipped_file_path)

    except Exception as e:
        logger.error(e)
        sys.exit(3)


def upload(data_path, bucket_name, bucket_path):
    """ Uploads data to a S3 bucket. This function does not return anything, it connects to the specified S3 bucket
        and uploads the file located at the data path variable and stores it at the bucket_path variable.
    Args:
        data_path:obj:`String` filepath to where the data is stored locally. Should be in the format of x.gz
        bucket_name:obj:`String` name of the S3 bucket located on AWS
        bucket_path:obj:`String` where the data should be saved on the S3 bucket. Should be in the format of x.json

    Returns:
        None
    """

    # Upload Data to S3
    try:
        logger.info("Beginning data upload to %s", bucket_name)
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket_name)
        bucket.upload_file(data_path, bucket_path)
        logger.info("Data has been successfully uploaded and can be found at %s", bucket_path)

    except botocore.exceptions.NoCredentialsError:
        logger.error("Your AWS credentials were not found. Be sure they were specified in the environment and passed "
                     "correctly into the Docker run command")
        sys.exit(3)

    except Exception as e:
        logger.error(e)
        sys.exit(3)
