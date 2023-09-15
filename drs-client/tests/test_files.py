from drs_client.files import compute_sha256


def test_compute_sha256(tmp_path):
    # GIVEN
    fname = tmp_path / "test.txt"
    _write(fname, "test file data")

    # WHEN/THEN
    assert compute_sha256(fname) == "1be7aaf1938cc19af7d2fdeb48a11c381dff8a98d4c4b47b3b0a5044a5255c04"  # noqa


def _write(fname, text):
    with open(fname, "wt") as fp:
        fp.write(text)
