import os

import pytest

from drs_client import upload
from drs_client.client import cli, ConfigManager


class MockBucketStore:

    call_args = []

    def __init__(self, *args, **kwds):
        pass

    def upload_file(self, fname):
        self.call_args.append(fname)
        return "http://example.com/myfile"


@pytest.fixture
def dummy_bucket_store(monkeypatch):
    monkeypatch.setattr(upload, "BucketStore", MockBucketStore)
    return MockBucketStore


class DummySubprocessRun:

    call_args = []

    def __call__(self, *args, **kwds):
        self.call_args.append((args, kwds))


@pytest.fixture
def dummy_subprocess_run(monkeypatch):
    from drs_client.download import subprocess

    dummy_run = DummySubprocessRun()
    monkeypatch.setattr(subprocess, "run", dummy_run)
    return dummy_run


def test_configure(cli_runner, tmp_path):

    # GIVEN
    config_file = tmp_path / "config.yaml"

    # WHEN
    result = cli_runner.invoke(
        cli, [
            "-c", config_file,
            "configure",
            "--secret-key", "SECRET",
            "--access-key", "ACCESS",
            "--bucket", "BUCKET",
            "--storage-url", "https://STORAGE",
            "--drs-url", "https://DRS",
        ])

    # THEN (a) check that command exited normally
    assert result.exit_code == 0

    # THEN (b) check that values were persisted correctly
    cfg = ConfigManager.from_file(config_file)
    assert cfg["secret_key"] == "SECRET"
    assert cfg["access_key"] == "ACCESS"
    assert cfg["bucket"] == "BUCKET"
    assert cfg["storage_url"] == "https://STORAGE"
    assert cfg["drs_url"] == "https://DRS"
    assert len(cfg) == 5


def test_upload_encrypt(
        cli_runner, tmp_path,
        dummy_bucket_store, dummy_drs_filer,
        drs_config, client_sk):

    # GIVEN
    upload_fname = tmp_path / "upload.txt"
    _write(upload_fname, "test")

    # WHEN
    result = cli_runner.invoke(
        cli, [
            "-c", drs_config,
            "upload",
            str(upload_fname),
            "--client-sk", client_sk
        ])

    # THEN (a) check that command exited normally
    assert result.exit_code == 0

    # THEN (b) check that bytes were uploaded
    assert len(dummy_bucket_store.call_args) == 1
    assert dummy_bucket_store.call_args[0].endswith("upload.txt.crypt4gh")

    # THEN (c) check that metatadata was registered
    assert dummy_drs_filer.call_count == 2
    payload = dummy_drs_filer.request_history[1].json()
    assert payload["name"] == "upload.txt.crypt4gh"


def test_upload_no_encrypt(
        cli_runner, tmp_path, dummy_bucket_store, dummy_drs_filer, drs_config):

    # GIVEN
    upload_fname = tmp_path / "upload.txt"
    _write(upload_fname, "test")

    # WHEN
    result = cli_runner.invoke(
        cli, [
            "-c", drs_config,
            "upload",
            str(upload_fname),
            "--no-encrypt"
        ])

    # THEN (a) check that command exited normally
    assert result.exit_code == 0

    # THEN (b) check that bytes were uploaded
    assert len(dummy_bucket_store.call_args) == 2
    assert dummy_bucket_store.call_args[1].endswith("upload.txt")

    # THEN (c) check that metatadata was registered
    assert dummy_drs_filer.call_count == 1
    payload = dummy_drs_filer.request_history[0].json()
    assert payload["name"] == "upload.txt"


def test_key_needed_for_encrypted_upload(cli_runner, tmp_path):

    # GIVEN
    upload_fname = tmp_path / "upload.txt"
    _write(upload_fname, "test")

    # WHEN
    result = cli_runner.invoke(
        cli, [
            "upload",
            str(upload_fname),
            "--encrypt",  # no client sk
        ])

    # THEN
    assert result.exit_code != 0
    assert result.stdout.startswith("Error: When uploading in encrypted mode")


def test_cannot_upload_encrypted_to_plain_server(
        cli_runner, tmp_path, dummy_drs_filer_plain, drs_config, client_sk):

    # GIVEN
    upload_fname = tmp_path / "upload.txt"
    _write(upload_fname, "test")

    # WHEN
    result = cli_runner.invoke(
        cli, [
            "-c", drs_config,
            "upload",
            str(upload_fname),
            "--encrypt",
            "--client-sk", client_sk,

        ], catch_exceptions=False)

    # THEN
    assert result.exit_code != 0
    assert "server does not advertise a Crypt4gh public key" in result.stdout


def test_download_file(
        cli_runner, drs_config, recipient_pk, dummy_subprocess_run):

    # GIVEN
    drs_id = "xyzzyx"

    # WHEN
    result = cli_runner.invoke(
        cli, [
            "-c", drs_config,
            "download",
            drs_id,
            "--recipient-pk", recipient_pk
        ]
    )

    # THEN (a) check that result exited cleanly
    assert result.exit_code == 0

    # THEN (b) check that drs command was invoked with the right args
    assert len(dummy_subprocess_run.call_args) == 1
    args = dummy_subprocess_run.call_args[0][0]
    assert args == (["drs", "get", "-d", "https://DRS", drs_id],)

    # THEN (c) check that pubkey was passed in environment
    assert os.environ.get("CRYPT4GH_PUBKEY") is not None


def _write(fname, text):
    with open(fname, "wt") as fp:
        fp.write(text)
