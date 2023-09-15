from base64 import b64encode

import click
import pytest

from crypt4gh_common import get_pubkey, get_seckey

from drs_client.upload import _get_server_pubkey, _load_crypt4gh_keys, KeyError
from drs_client.drs import DRSClient


def test_get_server_pubkey(dummy_drs_filer, service_info_crypt4gh):

    # GIVEN
    client = DRSClient("https://DRS")

    # WHEN
    pubkey = _get_server_pubkey(client)

    # THEN
    assert b64encode(pubkey).decode("ascii") == \
        service_info_crypt4gh["crypt4gh"]["pubkey"]


def test_get_server_pubkey_not_advertised(dummy_drs_filer_plain):

    # GIVEN
    client = DRSClient("https://DRS")

    # WHEN/THEN
    with pytest.raises(KeyError):
        _get_server_pubkey(client)


def test_load_crypt4gh_keys_no_client_sk(dummy_drs_filer):

    # GIVEN
    client = DRSClient("https://DRS")
    client_sk = "does-not-exist.key"

    # WHEN/THEN
    with pytest.raises(click.ClickException,
                       match="Could not load client secret key"):
        _load_crypt4gh_keys(client, client_sk)


def test_load_crypt4gh(dummy_drs_filer, server_pk, client_sk):

    # GIVEN
    client = DRSClient("https://DRS")

    # WHEN
    server_pubkey, client_seckey = _load_crypt4gh_keys(client, client_sk)

    # THEN
    expected_server_pubkey = get_pubkey(server_pk)
    expected_client_seckey = get_seckey(client_sk)
    assert server_pubkey == expected_server_pubkey
    assert client_seckey == expected_client_seckey
