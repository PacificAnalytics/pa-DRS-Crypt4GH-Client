import pytest

from drs_client import store
from drs_client.store import BucketStore


class MockBotoClient:

    upload_file_call_args = []
    download_file_call_args = []

    def generate_presigned_url(self, *args, **kwds):
        return "http://example.com/myfile.txt?Expiry=3600"

    def upload_file(self, *args, **kwds):
        self.upload_file_call_args.append((args, kwds))

    def download_file(self, *args, **kwds):
        self.download_file_call_args.append((args, kwds))


@pytest.fixture
def mock_boto3(monkeypatch):

    client = MockBotoClient()

    def configure_client(*args, **kwargs):
        return client

    monkeypatch.setattr(store, "_configure_client", configure_client)
    return client


def test_upload_file(tmp_path, mock_boto3):

    # GIVEN
    fname = tmp_path / "test.txt"
    _touch(fname)

    store = BucketStore("bucket")

    # WHEN
    obj_url = store.upload_file(fname, "file.txt")

    # THEN
    assert obj_url == "http://example.com/myfile.txt?Expiry=3600"
    assert len(mock_boto3.upload_file_call_args) == 1
    assert mock_boto3.upload_file_call_args[0][0] == (
        fname, "bucket", "file.txt"
    )


def test_download_file(mock_boto3):

    # GIVEN
    store = BucketStore("bucket")

    # WHEN
    store.download_file("fileid", "path/to/save.txt")

    # THEN
    assert len(mock_boto3.download_file_call_args) == 1
    assert mock_boto3.download_file_call_args[0][0] == (
        "bucket", "fileid", "path/to/save.txt"
    )


def _touch(fname):
    with open(fname, "wt"):
        pass
