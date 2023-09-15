import pathlib

import pytest


SERVICE_INFO_PLAIN = {
    "contactUrl": "contact/abc",
    "createdAt": "2020-01-01",
    "description": "Description of service.",
    "documentationUrl": "docs/abc",
    "environment": "ENV",
    "id": "TEMPID1",
    "name": "TEMP_STUB",
    "organization": {
        "name": "Parent organization",
        "url": "parent/abc"
    },
    "type": {
        "artifact": "TEMP_ARTIFACT",
        "group": "TEMP_GROUP",
        "version": "v1"
    },
    "updatedAt": "2020-01-01",
    "version": "0.0.0"
}
SERVICE_INFO_CRYPT4GH = {
    **SERVICE_INFO_PLAIN,
    "crypt4gh": {
            "pubkey": "AmEsb2n0m5mc6aadwpK4sT6zNapqgH+nnysNtpKa2Ag="
    },
}


def _configure_drs_filer(requests_mock, json):
    requests_mock.post("https://DRS/ga4gh/drs/v1/objects", text="\"dummy_id\"")
    requests_mock.get("https://DRS/ga4gh/drs/v1/service-info", json=json)


@pytest.fixture
def dummy_drs_filer(requests_mock):
    _configure_drs_filer(requests_mock, json=SERVICE_INFO_CRYPT4GH)
    yield requests_mock


@pytest.fixture
def dummy_drs_filer_plain(requests_mock):
    _configure_drs_filer(requests_mock, json=SERVICE_INFO_PLAIN)
    yield requests_mock


def _datapath(fname):
    return pathlib.Path(__file__).parent / "data" / fname


@pytest.fixture
def drs_config():
    return _datapath("drs-client-test.yaml")


@pytest.fixture
def client_sk():
    return _datapath("client-sk.key")


@pytest.fixture
def server_pk():
    return _datapath("server-pk.key")


@pytest.fixture
def recipient_pk():
    return _datapath("third-party-pk.key")


@pytest.fixture
def service_info_crypt4gh():
    return SERVICE_INFO_CRYPT4GH
