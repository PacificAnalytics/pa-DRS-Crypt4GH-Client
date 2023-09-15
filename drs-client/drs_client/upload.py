"""Crypt4gh-related utilities for the uploader client."""

from base64 import b64decode
import logging
import os
from pathlib import Path

import click

from .drs import DRSClient, DRSMetadata
from .store import BucketStore

from crypt4gh_common import encrypt as _encrypt, get_seckey

logger = logging.getLogger(__name__)


class KeyError(Exception):
    """Generic error if server pubkey could not be loaded."""


def upload_and_register(
        filename, drs_url, storage_url, bucket,
        encrypt=True, client_sk=None, desc=""):
    """Upload file to storage and register DRS metadata.

    Args:
        filename (str) : the path to the file to upload.
        drs_url (str) : the URL of the DRS server.
        storage_url (str) : the URL of the file storage.
        bucket (str) : the storage bucket to use.
        encrypt (bool) : whether to encrypt the file prior to upload.
        client_sk (str) : the path to the private key of the client.
        desc (str) : an optional description of the object.

    Returns:
        drs_id (str) : the DRS ID of the uploaded object.

    """
    drs_client = DRSClient(drs_url)
    # Encrypt byte data
    if encrypt:
        server_pubkey, client_seckey = _load_crypt4gh_keys(
            drs_client, client_sk)
        filename = _encrypt_crypt4gh_file(
            filename, client_seckey, server_pubkey)

    # Upload byte data to storage server
    store_client = BucketStore(bucket, endpoint=storage_url)
    store_client.upload_file(filename)
    resource_url = _create_s3_resource_url(
        bucket, os.path.basename(filename))

    # Upload metadata to DRS-filer
    metadata = DRSMetadata.from_file(
        filename, url=resource_url, description=desc)

    meta_id = drs_client.post_metadata(metadata)
    return meta_id


def _load_crypt4gh_keys(client, client_sk):
    """Load crypt4gh key data, or bail out if a problem occurred."""
    try:
        server_pubkey = _get_server_pubkey(client)
    except Exception:
        raise click.ClickException(
            "Encryption requested but server does not "
            "advertise a Crypt4gh public key.")

    try:
        client_seckey = get_seckey(client_sk)
    except Exception:
        raise click.ClickException(
            f"Could not load client secret key from location: {client_sk}."
            " Specify a valid key with the --client-sk flag.")

    return server_pubkey, client_seckey


def _get_server_pubkey(client):
    """Retrieve server public key, advertised in /service-info.

    Args:
        client (DRSClient) : DRS server client

    Returns:
        The public key of the server.
    """
    try:
        crypt4gh_info = client.get_service_info()["crypt4gh"]
        pubkey_b64 = crypt4gh_info["pubkey"]
        pubkey_decoded = b64decode(pubkey_b64)
        logger.info("Loaded server public key: %s", pubkey_b64)
    except Exception as e:
        raise KeyError() from e
    return pubkey_decoded


def _create_s3_resource_url(bucket, filename):
    return f"s3://{bucket}/{filename}"


def _encrypt_crypt4gh_file(filename, client_seckey, server_pubkey):
    """Encrypt file with given server/client keys."""
    filename = Path(filename)
    filename_enc = filename.with_suffix(filename.suffix + ".crypt4gh")
    with open(filename, "rb") as orig, open(filename_enc, "wb") as enc:
        _encrypt(client_seckey, server_pubkey, orig, enc)
    return str(filename_enc)
