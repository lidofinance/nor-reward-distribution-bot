import os
import subprocess
import time

import pytest
import variables
from contracts.extention import LidoContracts
from web3 import HTTPProvider
from web3_types import Web3


@pytest.fixture(scope='module')
def web3_integration(request):
    block_num = getattr(request, 'param', None)

    with anvil_fork(
        os.getenv('ANVIL_PATH', ''),
        variables.WEB3_RPC_ENDPOINTS[0],
        block_num,
    ):
        w3 = Web3(HTTPProvider('http://127.0.0.1:8545', request_kwargs={'timeout': 120}))
        w3.attach_modules({'lido': LidoContracts})
        yield w3


class anvil_fork:
    """
    --dump-state
    --load-state

    --state
    """

    def __init__(self, path_to_anvil, fork_url, block_number=None, port='8545'):
        self.path_to_anvil = path_to_anvil
        self.fork_url = fork_url
        self.port = port
        self.block_number = block_number

    def __enter__(self):
        block_command = tuple()
        if self.block_number is not None:
            block_command = ('--fork-block-number', str(self.block_number))

        self.process = subprocess.Popen(
            [
                f'{self.path_to_anvil}anvil',
                '-f',
                self.fork_url,
                '-p',
                self.port,
                *block_command,
                '--block-time',
                '12',
                '--auto-impersonate',
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        # Wait until server is ready
        time.sleep(4)
        return self.process

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.process.terminate()
