import logging
from functools import wraps
import time
from typing import Callable

from metrics.healthcheck import pulse
from metrics.metrics import ACCOUNT_BALANCE, LATEST_BLOCK_NUMBER, UNEXPECTED_EXCEPTIONS
from utils.timeout import TimeoutManager, TimeoutManagerError
from web3 import Web3
from web3.types import BlockData
from web3_multi_provider import NoActiveProviderError

import variables

logger = logging.getLogger(__name__)


def exception_handler(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except TimeoutManagerError as exception:
            logger.error({'msg': 'Timeout error.', 'error': str(exception), 'function': function.__name__})
            raise TimeoutManagerError('Bot stuck. Shut down.') from exception
        except NoActiveProviderError as exception:
            logger.error({'msg': 'No active node available. Shut down.', 'error': str(exception)})
            raise NoActiveProviderError from exception
        except Exception as error:
            logger.error({'msg': 'Unexpected error.', 'error': str(error), 'args': str(error.args)})
            UNEXPECTED_EXCEPTIONS.labels('exception').inc()

    return wrapper


class CycleHandler:
    SLOT_TIME = 12

    def __init__(
        self,
        w3: Web3,
        function: Callable[[BlockData], None],
        blocks_between_execution: int,
        cycle_max_lifetime_in_seconds: int,
    ):
        self.w3 = w3
        self._function = function
        self._blocks_between_execution = blocks_between_execution
        self._cycle_max_lifetime_in_seconds = cycle_max_lifetime_in_seconds

        self._next_expected_block_number = 0

    def execute_as_daemon(self) -> None:
        while True:
            self._wait_for_new_block_and_execute()

    def _wait_for_new_block_and_execute(self) -> None:
        pulse(variables.HEALTHCHECK_SERVER_PORT)
        if variables.ACCOUNT:
            balance = self.w3.eth.get_balance(variables.ACCOUNT.address)
            ACCOUNT_BALANCE.set(balance)

        latest_block = self._wait_until_next_block()
        self._execute_function(latest_block)

    @exception_handler
    def _wait_until_next_block(self) -> BlockData:
        expected_max_timeout = (self._blocks_between_execution + 10) * self.SLOT_TIME

        with TimeoutManager(expected_max_timeout):
            while True:
                latest_block: BlockData = self.w3.eth.get_block('latest')
                logger.debug({'msg': 'Fetch latest block.', 'value': latest_block})

                latest_block_number = latest_block.get('number', 0)
                LATEST_BLOCK_NUMBER.set(latest_block_number)

                if latest_block_number >= self._next_expected_block_number:
                    self._next_expected_block_number = latest_block_number + self._blocks_between_execution
                    return latest_block

                time_until_expected_block = (self._next_expected_block_number - latest_block_number) * self.SLOT_TIME
                logger.info({'msg': f'Sleep for {time_until_expected_block} seconds.'})

                time.sleep(time_until_expected_block)

    @exception_handler
    def _execute_function(self, block: BlockData) -> None:
        with TimeoutManager(self._cycle_max_lifetime_in_seconds):
            return self._function(block)
