import time
from unittest.mock import Mock

import pytest
from services.block_iterator import CycleHandler, exception_handler
from utils.timeout import TimeoutManagerError
from web3.types import BlockData
from web3_multi_provider import NoActiveProviderError

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ('expected_exception', 'result'),
    [
        (None, 'ignore'),
        (TimeoutManagerError, 'raise'),
        (NoActiveProviderError, 'raise'),
        (Exception, 'ignore'),
        (ValueError, 'ignore'),
    ],
)
def test_exception_handler(expected_exception, result):
    @exception_handler
    def func(exc):
        if exc is None:
            return

        raise exc

    if result == 'raise':
        with pytest.raises(expected_exception):
            func(expected_exception)
    else:
        func(expected_exception)


@pytest.fixture
def cycle_handler(web3_unit, request):
    func = getattr(request, 'func', lambda x: x)

    return CycleHandler(
        web3_unit,
        func,
        5,
        10,
    )


def test_execute_as_daemon(cycle_handler):
    def cycle():
        call_count = getattr(cycle, 'call_count', 0)
        cycle.call_count = call_count + 1  # type: ignore

        if call_count == 5:
            raise StopIteration

    cycle_handler._wait_for_new_block_and_execute = cycle

    with pytest.raises(StopIteration):
        cycle_handler.execute_as_daemon()

    assert cycle.call_count == 6  # type: ignore


def test_wait_for_new_block_and_execute(cycle_handler, set_account):
    cycle_handler.w3.eth.get_balance = Mock(return_value=0)
    cycle_handler._wait_until_next_block = Mock(return_value='block')
    cycle_handler._execute_function = Mock()

    cycle_handler._wait_for_new_block_and_execute()

    cycle_handler.w3.eth.get_balance.assert_called_once()
    cycle_handler._execute_function.assert_called_once()


def test_wait_until_next_block(cycle_handler, mock_sleep):
    cycle_handler._blocks_between_execution = 2
    cycle_handler._next_expected_block_number = 5
    cycle_handler.w3.eth.get_block = Mock(side_effect=[BlockData(number=0), BlockData(number=5)])  # type: ignore

    cycle_handler._wait_until_next_block()

    time.sleep.assert_called_with(12 * 5)  # type: ignore
    assert cycle_handler._next_expected_block_number == 7


def test_execute_function(cycle_handler):
    bd = BlockData()
    cycle_handler._function = Mock()
    cycle_handler._execute_function(bd)
    cycle_handler._function.assert_called_once_with(bd)


def test_timeout(cycle_handler):
    cycle_handler._cycle_max_lifetime_in_seconds = 1
    cycle_handler._function = lambda x: time.sleep(3)
    with pytest.raises(TimeoutManagerError):
        cycle_handler._execute_function(BlockData())
