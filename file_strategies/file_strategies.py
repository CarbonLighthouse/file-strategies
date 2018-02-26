"""
Strategy classes for access to various file sources (S3, Local, etc.)
"""

import errno
import os
from io import StringIO
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError


class LocalFile(object):
    """
    File strategy for local file
    """
    def __init__(self, path):
        self.path = path
        self.protocol = 'file://'
        self.basename = os.path.basename(path)
        self.dir_path = os.path.dirname(path)
        self.url = self.protocol + path

    def get_contents(self):
        with open(self.path) as stream:
            return StringIO(stream.read())

    def put_contents(self, body):
        if not os.path.exists(os.path.dirname(self.path)):
            try:
                os.makedirs(os.path.dirname(self.path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(self.path, 'w') as stream:
            stream.write(body)

    def exists(self):
        return os.path.exists(self.path)


class S3File(object):
    """
    File strategy for S3 objects
    """
    def __init__(self, path, bucket, s3):
        self.path = path.strip('/')
        self.bucket = bucket
        self.s3 = s3
        self.protocol = 's3://'
        path_parts = self.path.split('/')
        self.basename = path_parts.pop()
        self.dir_path = '/'.join([bucket] + path_parts)
        self.url = self.protocol + self.dir_path + '/' + self.basename

    def get_contents(self):
        response = self.s3.Object(self.bucket, self.path).get()
        return response['Body']

    def put_contents(self, body):
        self.s3.Object(self.bucket, self.path).put(Body=body)

    def exists(self):
        try:
            self.s3.Object(self.bucket, self.path).load()
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                exists = False
            else:
                raise
        else:
            exists = True

        return exists


def is_valid_url(url):
    """
    Returns true if the given string is a file:// or s3:// url
    :param str url:
    :return:
    """
    return url.startswith('file://') or url.startswith('s3://')


def make_file(path):
    """
    Factory function for File strategies

    :param str path: A local relative path or s3://, file:// protocol urls
    :return:
    """
    try:
        if not is_valid_url(path):
            return LocalFile(os.path.abspath(path))

        url_obj = urlparse(path)

        if url_obj.scheme == 'file':
            return LocalFile(url_obj.path)
        elif url_obj.scheme == 's3':
            return S3File(url_obj.path, url_obj.netloc, boto3.resource('s3'))

        raise
    except Exception:
        raise ValueError('Path %s is not a valid file or s3 url' % path)
