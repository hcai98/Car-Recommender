import argparse
import logging.config
import os

from src.utils.s3 import download_file_from_s3
from src.utils.s3 import upload_file_to_s3

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('upload_data')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', default=False, action='store_true',
                        help="If used, will load data via pandas")
    parser.add_argument('--s3path', default=None,
                        help="If used, will load data via pandas")
    parser.add_argument('--local_path', default=None,
                        help="Where to load data to in S3")
    args = parser.parse_args()


    if args.download:
        # download file from s3
        download_file_from_s3(args.local_path, args.s3path)
    else:
        # upload a single file
        upload_file_to_s3(args.local_path, args.s3path)
