# file-strategies
Strategy classes for access to various file sources (S3, local, etc.) under a common interface. Python 3 compatible.

## Setup

```bash
pip install .
```

## Usage
`make_file` returns either an S3File or LocalFile object, both of which implement the same interface with functions
`get_contents` and `put_contents`.
```python
my_local_or_s3_file = make_file(my_file_path)
my_file_contents = my_local_or_s3_file.get_contents()
my_local_or_s3_file.put_contents('beep boop')
```
