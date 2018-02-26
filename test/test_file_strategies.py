"""
Tests for file strategies (S3, Local, etc.) and helper methods
"""

import os
import unittest

from botocore.exceptions import ClientError
from unittest.mock import MagicMock
from testfixtures import TempDirectory

from file_strategies.file_strategies import LocalFile, S3File, make_file


class TestLocalFile(unittest.TestCase):
    """
    python -m unittest -v test.util.test_file_strategies.TestLocalFile
    """
    def setUp(self):
        self.tmp_dir = TempDirectory()
        self.tmp_dir.write('foo.txt', 'bar', encoding='utf-8')

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_attributes(self):
        """should build attribute data to describe file"""
        path = os.path.join(self.tmp_dir.path, 'foo.txt')
        subject = LocalFile(path)

        self.assertEqual(subject.protocol, 'file://')
        self.assertEqual(subject.basename, 'foo.txt')
        self.assertEqual(subject.dir_path, self.tmp_dir.path)

    def test_get_contents(self):
        """should return contents from local file"""
        path = os.path.join(self.tmp_dir.path, 'foo.txt')
        subject = LocalFile(path)

        actual = subject.get_contents().getvalue()
        expected = 'bar'

        self.assertEqual(actual, expected)

    def test_put_contents(self):
        """should store contents to local file"""
        path = os.path.join(self.tmp_dir.path, 'my_dir', 'foo.txt')
        subject = LocalFile(path)

        subject.put_contents('baz')
        actual = self.tmp_dir.read('my_dir/foo.txt', encoding='utf-8')
        expected = 'baz'

        self.assertEqual(actual, expected)

    def test_exists(self):
        """should determine if a local file exists or not"""
        present_path = os.path.join(self.tmp_dir.path, 'foo.txt')
        absent_path = os.path.join(self.tmp_dir.path, 'missing.txt')
        present_subject = LocalFile(present_path)
        absent_subject = LocalFile(absent_path)

        self.assertTrue(present_subject.exists())
        self.assertFalse(absent_subject.exists())


class TestS3File(unittest.TestCase):
    """
    python -m unittest -v test.util.test_file_strategies.TestS3File
    """

    def test_attributes(self):
        """should build attribute data to describe file"""
        path = 'foo/bar.txt'
        bucket = 'test_bucket'
        s3 = MagicMock()
        subject = S3File(path, bucket, s3)

        self.assertEqual(subject.protocol, 's3://')
        self.assertEqual(subject.basename, 'bar.txt')
        self.assertEqual(subject.dir_path, 'test_bucket/foo')
        self.assertEqual(subject.url, 's3://test_bucket/foo/bar.txt')

    def test_get_contents(self):
        """should get contents from an s3 object"""
        path = 'foo.txt'
        bucket = 'test_bucket'
        s3 = MagicMock()
        object_mock = MagicMock()
        object_mock.get.return_value = {'Body': 'test_body'}
        s3.Object.return_value = object_mock

        subject = S3File(path, bucket, s3)

        actual = subject.get_contents()
        expected = 'test_body'

        self.assertEqual(actual, expected)
        s3.Object.assert_called_once_with(bucket, path)

    def test_put_contents(self):
        """should put contents to an s3 object"""
        path = 'foo.txt'
        bucket = 'test_bucket'
        s3 = MagicMock()
        object_mock = MagicMock()
        s3.Object.return_value = object_mock

        subject = S3File(path, bucket, s3)

        subject.put_contents('test_body')

        s3.Object.assert_called_once_with(bucket, path)
        object_mock.put.assert_called_once_with(Body='test_body')

    def test_s3_key_exists(self):
        """should return true if an s3 key exists"""
        path = 'foo.txt'
        bucket = 'test_bucket'
        s3 = MagicMock()
        object_mock = MagicMock()
        object_mock.load.side_effect = {'load': 'result'}
        s3.Object.return_value = object_mock

        subject = S3File(path, bucket, s3)

        self.assertTrue(subject.exists())

    def test_s3_key_not_exists(self):
        """should return false if an s3 key does not exist"""
        path = 'foo.txt'
        bucket = 'test_bucket'
        s3 = MagicMock()
        object_mock = MagicMock()
        object_mock.load.side_effect = ClientError({'Error': {'Code': '404'}}, 'HeadObject')
        s3.Object.return_value = object_mock

        subject = S3File(path, bucket, s3)

        self.assertFalse(subject.exists())


class TestMakeFile(unittest.TestCase):
    """
    python -m unittest -v test.util.test_file_strategies.TestMakeFile
    """
    def test_make_local_from_relative_path(self):
        """should create a local file when given a relative path"""
        cwd = os.getcwd()

        with TempDirectory() as d:
            os.chdir(d.path)

            rel_path = './foo.txt'
            actual = make_file(rel_path)
            expected = LocalFile(os.path.abspath('./foo.txt'))

            self.assertEqual(actual.__dict__, expected.__dict__)

        os.chdir(cwd)

    def test_make_local_file_from_windows_path(self):
        """should create a local file when given a windows path"""

        path = 'C:\\Users\\User\\.octorc'
        actual = make_file(path)
        expected = LocalFile(os.path.abspath(path))

        self.assertEqual(actual.__dict__, expected.__dict__)

    def test_make_local_file_from_file_url(self):
        """should create a local file when given a file:// protocol url"""

        path = '/path/to/foo.txt'
        url = 'file://' + path
        actual = make_file(url)
        expected = LocalFile(path)

        self.assertEqual(actual.__dict__, expected.__dict__)

    def test_make_s3_file_from_s3_url(self):
        """should make S3File instance when give s3 url"""
        url = 's3://test_bucket/foo.txt'
        actual = make_file(url)

        self.assertIsInstance(actual, S3File)

    def test_raise_value_error(self):
        """should raise a value error if given invalid url or path"""
        invalid_path = 42
        self.assertRaises(ValueError, make_file, invalid_path)
