from dataclasses import dataclass
import pathlib

import pytest

from crypt4gh_common import get_pubkey, get_seckey


def _datapath(fname):
    return pathlib.Path(__file__).parent / "data" / fname


@dataclass
class Keys:

    CLIENT_PK = get_pubkey(_datapath("client-pk.key"))
    CLIENT_SK = get_seckey(_datapath("client-sk.key"))
    SERVER_PK = get_pubkey(_datapath("server-pk.key"))
    SERVER_SK = get_seckey(_datapath("server-sk.key"))
    RECIPIENT_PK = get_pubkey(_datapath("third-party-pk.key"))
    RECIPIENT_SK = get_seckey(_datapath("third-party-sk.key"))


@pytest.fixture
def keys():
    return Keys()
