# Crypt4GH common functionality

This folder contains a small Python package with a public API for low-level operations implemented in the [Crypt4GH package](https://crypt4gh.readthedocs.io/en/latest/index.html). For the most part, the API exposed here just wraps a corresponding private API in the Crypt4GH package.

Supported operations:

- Loading a private or public key from a file.
- Encrypting a file.
- Re-encrypting an encrypted file.


## Installing the package

From the package root (the folder that this README is in), run
```bash
pip install -e . -v
```

To run the tests, install the optional `test` dependencies:
```bash
pip install -e '.[test]' -v
```


## Running the tests 

From the package root, run
```bash
pytest
```


## License

This package is licensed under the [Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0).
