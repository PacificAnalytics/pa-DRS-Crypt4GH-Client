# DRS Crypt4GH client

This folder contains a simple DRS client with support for Crypt4GH-encrypted uploading and downloading.

## Installing the package

First, install the `crypt4gh-common` package, also in this repo.

Then, from the package root (the folder that this README is in), run
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


## Using the client

The client application needs a few configuration details before it can be
used. Run the following command, and answer the prompts as they appear on the
command line:
```
drs-client configure
```
This process needs to happen only once.

Once configuration is complete, the application will write a configuration file
named `drs-client.yaml` to the current directory. To change the location of
configuration file, invoke the application with the `-c` option to specify an
alternate location.

To upload a file, invoke the application as follows:
```bash
drs-client upload <path/to/file.dat> --client-sk client.sk
```
This will print a number of status messages, followed by the DRS ID of the
uploaded object when the upload is successful. This ID is what is used to refer
to file when requesting it for download.

The flag `--client-sk` specifies the client secret key to sign the file. To
generate a client public/secret keypair, run the following command:
```bash
crypt4gh-keygen --sk client.sk --pk client.pk
```

To download a file, given its DRS ID, run
```bash
drs-client download <drs-id> --recipient-pk recipient.pk
```

Here, `--recipient-pk` specifies the public key of the recipient. The
downloaded file will be Crypt4GH-encrypted with this key, and placed in a
folder named after the DRS ID.

A public/secret keypair for the recipient may be generated by running
```bash
crypt4gh-keygen --sk recipient.sk --pk recipient.pk
```

To decrypt the downloaded file, `cd` into the directory named after the DRS ID,
and run
```
crypt4gh decrypt --sk <path/to/recipient.sk> < <downloaded-file.crypt4gh>
```
This will print the contents of the decrypted file to stdout; redirect to a
file if this is not desired (e.g. when downloading a binary file).


## License

This package is licensed under the [Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0).
