# RAISE Enclave

This repo contains code, documentation, and examples related to data enclave support for the RAISE project.

## Research users

Research users can find details on how to use RAISE enclaves [here](./docs/usage.md).

## Developers

When developing code for this repo, developers may want to install the project in editable mode:

```bash
$ pip install -e .
```

The code can be linted and tested locally as well:

```bash
$ pip install .[test]
$ flake8
$ pytest
```

Code coverage reports can be generated when running tests:

```bash
$ pytest --cov=enclave_mgmt --cov-report=term --cov-report=html
```

## Compile Models

The compile models script is designed to facilitate the process of data collection and validation for researchers.

### File descriptions

1. **compile_models.py**
* This script serves as the entry point. It orchestrates the execution of various components.

2. **collect_data.py**
* The `collect_data.py` script leverages the `boto3` library to interact with S3 and uses the `pandas` library to create dataframes for subsequent processing.

3. **create_models.py**
* The `create_models.py` script takes the data collected by `collect_data.py` and transforms it to be used in the Pydantic models. This process also validates the data.

4. **models.py**
* The `models.py` script acts as a centralized location for storing the Pydantic models. 
