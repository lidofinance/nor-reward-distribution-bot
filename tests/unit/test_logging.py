import importlib
import json
import logging
import sys

import pytest
import variables
from logmask import JsonFormatter, SafeStreamHandler

pytestmark = pytest.mark.unit

RPC = 'https://rpc.example/v3/secret-key-1'
KEY = '0x' + 'ab' * 32


@pytest.fixture
def root_logger(monkeypatch):
    """The logging of the bot configured from an environment with secrets, as at startup."""
    monkeypatch.setenv('WEB3_RPC_ENDPOINTS', RPC)
    monkeypatch.setenv('WALLET_PRIVATE_KEY', KEY)
    importlib.reload(variables)
    import metrics.logging

    importlib.reload(metrics.logging)
    yield logging.getLogger()
    monkeypatch.undo()
    importlib.reload(variables)


def test_log_lines_are_json_with_private_values_masked(root_logger):
    # pytest adds its own capture handlers to the root logger around every test; the bot's handler is the only stream one.
    (handler,) = (h for h in root_logger.handlers if isinstance(h, SafeStreamHandler))
    assert isinstance(handler.formatter, JsonFormatter)

    record = logging.LogRecord(
        'test', logging.ERROR, __file__, 1, {'msg': 'RPC failed', 'url': RPC, 'path': '/v3/secret-key-1', 'key': KEY}, None, None
    )
    line = handler.format(record)

    assert 'secret-key' not in line
    assert KEY not in line
    assert json.loads(line)['msg'] == 'RPC failed'


def test_unhandled_exceptions_go_through_the_logger(root_logger):
    assert sys.excepthook is not sys.__excepthook__
