import logging
import signal

import pytest
from main import shutdown

pytestmark = pytest.mark.unit


def test_shutdown_logs_the_signal_and_exits_with_zero(caplog):
    with caplog.at_level(logging.INFO, logger='main'), pytest.raises(SystemExit) as exit_info:
        shutdown(signal.SIGTERM, None)

    assert exit_info.value.code == 0
    assert caplog.records[-1].msg == {'msg': 'SIGTERM received. Shut down.'}
