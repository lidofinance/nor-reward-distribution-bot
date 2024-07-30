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

NODE_OPERATOR_REGISTRY_ADDRESSES = os.environ['NODE_OPERATOR_REGISTRY_ADDRESSES'].split(',')

WEB3_RPC_ENDPOINTS = os.environ['WEB3_RPC_ENDPOINTS'].split(',')

PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', 9000))
HEALTHCHECK_SERVER_PORT = int(os.getenv('HEALTHCHECK_SERVER_PORT', 9010))

PUBLIC_ENV_VARS = {
    'PROMETHEUS_PORT': PROMETHEUS_PORT,
    'HEALTHCHECK_SERVER_PORT': HEALTHCHECK_SERVER_PORT,
    'NODE_OPERATOR_REGISTRY_ADDRESSES': NODE_OPERATOR_REGISTRY_ADDRESSES,
    'ACCOUNT': '' if ACCOUNT is None else ACCOUNT.address,
}

PRIVATE_ENV_VARS = {
    'WEB3_RPC_ENDPOINTS': WEB3_RPC_ENDPOINTS,
    'WALLET_PRIVATE_KEY': WALLET_PRIVATE_KEY,
}

assert not set(PRIVATE_ENV_VARS.keys()).intersection(set(PUBLIC_ENV_VARS.keys()))
