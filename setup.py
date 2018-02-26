
from setuptools import setup, find_packages

setup(
    name='file_strategies',
    version='0.0.0',
    url='https://github.com/CarbonLighthouse/file_strategies',
    author='CarbonLighthouse',
    description='Strategy classes for access to various file sources (S3, local, etc.). '
                'Python 2/3 compatible.',
    long_description="See: https://github.com/CarbonLighthouse/file_strategies",
    keywords='s3 file aws s3file fs local',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'boto3==1.4.7',
        'future==0.16.0'
    ]
)
