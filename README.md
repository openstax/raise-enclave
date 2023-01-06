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

