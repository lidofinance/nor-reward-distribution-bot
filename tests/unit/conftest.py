from unittest.mock import Mock

import pytest
from web3_types import Web3


@pytest.fixture
def web3_unit():
    w3 = Web3()
    w3.lido = Mock()
    return w3
