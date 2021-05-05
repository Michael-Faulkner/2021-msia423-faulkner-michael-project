import requests
import boto3
import logging


def download(url, gzip_save_path):
    with open(gzip_save_path, "wb") as f:
        r = requests.get(url)
        f.write(r.content)


def upload(data_path, bucket_name, bucket_path):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    bucket.upload_file(data_path, bucket_path)
