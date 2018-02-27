
from setuptools import setup, find_packages

setup(
    name='file-strategies',
    version='0.0.1',
    url='https://github.com/CarbonLighthouse/file-strategies',
    author='CarbonLighthouse',
    description='Strategy classes for access to various file sources (S3, local, etc.). '
                'Python 3 compatible.',
    long_description="See: https://github.com/CarbonLighthouse/file-strategies",
    keywords='s3 file aws s3file fs local',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3',
    install_requires=[
        'boto3>=1.4.7, <=1.6.0'
    ]
)
