from unittest.mock import Mock

import pytest
from web3 import Account
import time

import variables


@pytest.fixture
def set_account():
    variables.ACCOUNT = Account.from_key('0' * 63 + '1')
    yield
    variables.ACCOUNT = None


@pytest.fixture
def mock_sleep():
    sleep = time.sleep
    time.sleep = Mock()
    yield
    time.sleep = sleep
