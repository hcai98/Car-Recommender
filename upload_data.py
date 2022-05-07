import argparse
import logging.config
import os

from src.s3 import download_file_from_s3
from src.s3 import upload_file_to_s3, upload_dir_to_s3

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('upload_data')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', default=False, action='store_true',
                        help="If used, will load data via pandas")
    parser.add_argument('--directory', default=False, action='store_true',
                        help="Upload a directory")
    parser.add_argument('--s3path', default='s3://msia423-cai-haoayang/raw/',
                        help="If used, will load data via pandas")
    parser.add_argument('--local_path', default='data/vegas.csv',
                        help="Where to load data to in S3")
    args = parser.parse_args()


    if args.download:
        download_file_from_s3(args.local_path, args.s3path)
    else:
        if args.directory:
            # upload a directory recursively to s3
            upload_dir_to_s3(args.local_path, args.s3path)
        else:
            # upload a single file
            upload_file_to_s3(args.local_path, args.s3path)
