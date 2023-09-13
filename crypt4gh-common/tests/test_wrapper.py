from io import BytesIO

import crypt4gh
import pytest

from crypt4gh_common import encrypt, reencrypt, EncryptionError


def test_encrypt(keys):
    # Given (unencrypted data)
    file_data = BytesIO(b"test data")

    # When (encrypt data for recipient)
    encrypted_data = BytesIO()
    encrypt(keys.CLIENT_SK, keys.RECIPIENT_PK, file_data, encrypted_data)

    # Then (assert recipient can decrypt)
    encrypted_data.seek(0)
    assert _decrypt(encrypted_data, keys.RECIPIENT_SK) == b"test data"


def test_encrypt_fails_gracefully(keys):
    # Given (unencrypted data)
    file_data = BytesIO(b"test data")

    # When (attempting to encrypt with faulty key)
    with pytest.raises(EncryptionError):
        encrypt(b"xyz", keys.RECIPIENT_PK, file_data, BytesIO())


def test_reencrypt(keys):
    # Given (encrypted data by client for server)
    file_data = BytesIO(b"test data")
    encrypted_data = BytesIO()
    encrypt(keys.CLIENT_SK, keys.SERVER_PK, file_data, encrypted_data)
    encrypted_data.seek(0)

    # When (reencrypt on server for third-party)
    reencrypted_data = BytesIO()
    reencrypt(
        keys.SERVER_SK, keys.RECIPIENT_PK, encrypted_data, reencrypted_data)

    # Then (third party can decrypt)
    reencrypted_data.seek(0)
    assert _decrypt(reencrypted_data, keys.RECIPIENT_SK) == b"test data"


def test_reencrypt_fails_gracefully(keys):
    # Given (unencrypted data)
    file_data = BytesIO(b"test data")

    # When (attempting to reencrypt unencrypted data)
    with pytest.raises(EncryptionError):
        reencrypt(keys.SERVER_SK, keys.RECIPIENT_PK, file_data, BytesIO())


def _decrypt(buf, seckey):
    buf_out = BytesIO()
    crypt4gh.lib.decrypt([(0, seckey, None)], buf, buf_out)
    return buf_out.getvalue()
