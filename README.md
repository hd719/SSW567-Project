# SSW567-Project

MRTD (Machine-Readable Travel Document) system for encoding, decoding, and validating passport MRZ data using Fletcher-16 checksums.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (for dependency management)

## Setup

```bash
uv venv
source .venv/bin/activate
uv pip install coverage
```

## Running Tests

```bash
python -m unittest MTTDtest -v
```

## Coverage

```bash
coverage run -m unittest MTTDtest
coverage report -m --include=MRTD.py
```
