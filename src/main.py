import variables
from bots.distributor import RewardLiquidationBot
from contracts.extention import LidoContracts
from metrics.healthcheck import start_pulse_server
from metrics.logging import logging
from metrics.requests_metric_middleware import add_requests_metric_middleware
from prometheus_client import start_http_server
from services.block_iterator import CycleHandler
from web3_multi_provider import MultiProvider
from web3_types import Web3

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logger.info({'msg': 'Start Reward distribution bot.'})

    logger.info({'msg': f'Start up healthcheck service on port: {variables.HEALTHCHECK_SERVER_PORT}.'})
    start_pulse_server(variables.HEALTHCHECK_SERVER_PORT)

    logger.info({'msg': f'Start up metrics service on port: {variables.PROMETHEUS_PORT}.'})
    start_http_server(variables.PROMETHEUS_PORT)

    logger.info({'msg': 'Connect MultiProvider.'})
    web3 = Web3(MultiProvider(variables.WEB3_RPC_ENDPOINTS))

    add_requests_metric_middleware(web3)

    web3.attach_modules({'lido': LidoContracts})
    bot = RewardLiquidationBot(web3)

    ch = CycleHandler(
        web3,
        bot.execute,
        32,
        120,
    )
    ch.execute_as_daemon()
