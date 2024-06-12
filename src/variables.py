import logging
import os

from eth_account import Account

logger = logging.getLogger(__name__)


WALLET_PRIVATE_KEY = os.getenv('WALLET_PRIVATE_KEY', None)

if WALLET_PRIVATE_KEY:
    ACCOUNT = Account.from_key(WALLET_PRIVATE_KEY)
    logger.info({'msg': 'Load account from private key.', 'value': ACCOUNT.address})
else:
    ACCOUNT = None
    logger.warning({'msg': 'Account is not provided. Dry mode.'})


NODE_OPERATOR_REGISTRY_ADDRESS = os.environ['NODE_OPERATOR_REGISTRY_ADDRESS']

WEB3_RPC_ENDPOINTS = os.environ['WEB3_RPC_ENDPOINTS'].split(',')

PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', 9000))
HEALTHCHECK_SERVER_PORT = int(os.getenv('HEALTHCHECK_SERVER_PORT', 9010))
