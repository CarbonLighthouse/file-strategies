# file-strategies
[![Build Status](https://travis-ci.org/CarbonLighthouse/file-strategies.svg?branch=master)](https://travis-ci.org/CarbonLighthouse/file-strategies)
[![Coverage Status](https://coveralls.io/repos/github/CarbonLighthouse/file-strategies/badge.svg?branch=master)](https://coveralls.io/github/CarbonLighthouse/file-strategies?branch=master)

Strategy classes for access to various file sources (S3, local, etc.) under a common interface. Python 3 compatible.

## Setup

```bash
pip install .
```

## Usage
`make_file` returns either an S3File or LocalFile object, both of which implement the same interface with functions
`get_contents` and `put_contents`.
```python
from file_strategies import make_file
  
my_local_or_s3_file = make_file(my_file_path)
my_file_contents = my_local_or_s3_file.get_contents()
my_local_or_s3_file.put_contents('beep boop')
```
