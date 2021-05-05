import boto3


def upload(data_path, bucket_name, bucket_path):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    bucket.upload_file(data_path, bucket_path)
