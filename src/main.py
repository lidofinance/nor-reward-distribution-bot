import signal
import sys
from types import FrameType

import variables
from bots.distributor import RewardLiquidationBot
from contracts.extention import LidoContracts
from metrics.healthcheck import start_pulse_server
from metrics.logging import logging
from prometheus_client import start_http_server
from services.block_iterator import CycleHandler
from web3_multi_provider import MultiProvider, init_metrics
from web3_types import Web3

logger = logging.getLogger(__name__)


def shutdown(signum: int, frame: FrameType | None) -> None:
    """Exit cleanly on SIGTERM/SIGINT. As PID 1 in a container the process would ignore the signal and get SIGKILL."""
    logger.info({'msg': f'{signal.Signals(signum).name} received. Shut down.'})
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    logger.info({'msg': 'Start Reward distribution bot.', 'build': variables.BUILD_INFO})
    logger.info({'msg': 'Bot env variables', 'value': variables.env_vars_for_log()})

    if variables.ACCOUNT is None:
        logger.warning({'msg': 'Account is not provided. Dry mode: transactions are not sent.'})
    else:
        logger.info({'msg': 'Load account from private key.', 'value': variables.ACCOUNT.address})

    start_pulse_server(variables.HEALTHCHECK_SERVER_HOST, variables.HEALTHCHECK_SERVER_PORT)
    start_http_server(variables.PROMETHEUS_PORT)

    logger.info({'msg': 'Connect MultiProvider.'})
    init_metrics()
    web3 = Web3(MultiProvider(variables.WEB3_RPC_ENDPOINTS))
    web3.attach_modules({'lido': LidoContracts})
    bot = RewardLiquidationBot(web3)

    ch = CycleHandler(
        web3,
        bot.execute,
        variables.BLOCKS_BETWEEN_EXECUTION,
        120,
    )
    ch.execute_as_daemon()
