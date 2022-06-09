import logging
import re
import typing

import boto3
import botocore

logger = logging.getLogger(__name__)

def parse_s3(s3path: str) -> typing.Tuple[str, str]:
    """Parse s3 bucket name and file path on s3 from the
    full s3 path.

    Args:
        s3path (str): The full S3 path to file.

    Returns:
        typing.Tuple[str, str]:
            s3bucket: name of the s3 bucket.
            s3path: relative path to the file on s3.
    """
    regex = r's3://([\w._-]+)/([$\w./_-]+)'

    matched = re.match(regex, s3path)
    s3bucket = matched.group(1)
    s3path = matched.group(2)

    return s3bucket, s3path

def upload_file_to_s3(local_path: str, s3path: str) -> None:
    """Upload files in a local path to a location on S3

    Args:
        local_path (str): Local path to the file.
        s3path (str): Where to save the file on s3.
    """
    s3bucket, s3_just_path = parse_s3(s3path)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(s3bucket)

    try:
        bucket.upload_file(local_path, s3_just_path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info('Data uploaded from %s to %s', local_path, s3path)

def download_file_from_s3(local_path: str, s3path: str) -> None:
    """Download file from s3 to local directories.

    Args:
        local_path (str): Where the file will be saved on the local machine.
        s3path (str): S3 path to the file.
    """
    s3bucket, s3_just_path = parse_s3(s3path)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(s3bucket)

    try:
        bucket.download_file(s3_just_path, local_path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info('Data downloaded from %s to %s', s3path, local_path)
