import datetime

from drs_client.drs import DRSClient, DRSMetadata, _create_request_data


def _is_iso8601(s):
    try:
        datetime.datetime.fromisoformat(s)
        return True
    except ValueError:
        return False


def test_drs_metadata(tmp_path):
    # GIVEN
    checksum = "1be7aaf1938cc19af7d2fdeb48a11c381dff8a98d4c4b47b3b0a5044a5255c04"  # noqa
    fname = tmp_path / "test.txt"
    _write(fname, "test file data")

    # WHEN
    drs_metadata = DRSMetadata.from_file(fname)

    # THEN
    assert drs_metadata.checksum == checksum
    assert drs_metadata.size == 14


def test_create_request_data():

    # GIVEN
    drs_metadata = DRSMetadata(
        name="obj",
        description="an object",
        checksum="xyz",
        url="http://url.to",
        size=25)

    # WHEN
    rdata = _create_request_data(drs_metadata)

    # THEN
    assert rdata["name"] == "obj"
    assert rdata["description"] == "an object"
    assert rdata["access_methods"][0]["access_url"]["url"] == "http://url.to"
    assert rdata["checksums"][0]["checksum"] == "xyz"
    assert rdata["size"] == 25
    assert _is_iso8601(rdata["created_time"])
    assert _is_iso8601(rdata["updated_time"])


def test_post_metadata(dummy_drs_filer, tmp_path):

    # GIVEN
    drs_client = DRSClient("https://DRS")

    fname = tmp_path / "test.txt"
    _write(fname, "test file data")

    # WHEN
    drs_meta = DRSMetadata.from_file(fname)
    response = drs_client.post_metadata(drs_meta)

    # THEN
    assert response == "dummy_id"


def test_get_service_info(dummy_drs_filer, service_info_crypt4gh):

    # GIVEN
    drs_client = DRSClient("https://DRS")

    # WHEN
    actual = drs_client.get_service_info()

    # THEN
    assert actual == service_info_crypt4gh


def _write(fname, text):
    with open(fname, "wt") as fp:
        fp.write(text)
