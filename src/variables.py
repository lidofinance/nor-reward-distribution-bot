import os

from eth_account import Account
from utils.build_info import load_build_info
from utils.secrets import MASKED_VALUE

WALLET_PRIVATE_KEY = os.getenv('WALLET_PRIVATE_KEY', None)

# Without the key the bot runs in dry mode: it checks the distribution state and logs, but does not send transactions.
ACCOUNT = Account.from_key(WALLET_PRIVATE_KEY) if WALLET_PRIVATE_KEY else None

NODE_OPERATOR_REGISTRY_ADDRESSES = os.environ['NODE_OPERATOR_REGISTRY_ADDRESSES'].split(',')
STETH_ADDRESS = os.environ['STETH_ADDRESS']

WEB3_RPC_ENDPOINTS = os.environ['WEB3_RPC_ENDPOINTS'].split(',')

PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', 9000))
# All interfaces by default, so that the health check is reachable from outside the container (Kubernetes probes).
HEALTHCHECK_SERVER_HOST = os.getenv('HEALTHCHECK_SERVER_HOST', '0.0.0.0')
HEALTHCHECK_SERVER_PORT = int(os.getenv('HEALTHCHECK_SERVER_PORT', 9010))

BLOCKS_BETWEEN_EXECUTION = int(os.getenv('BLOCKS_BETWEEN_EXECUTION', 1))
MIN_SHARES_TO_DISTRIBUTE = int(os.getenv('MIN_SHARES_TO_DISTRIBUTE', 10**9))

BUILD_INFO = load_build_info()

PUBLIC_ENV_VARS = {
    'PROMETHEUS_PORT': PROMETHEUS_PORT,
    'HEALTHCHECK_SERVER_HOST': HEALTHCHECK_SERVER_HOST,
    'HEALTHCHECK_SERVER_PORT': HEALTHCHECK_SERVER_PORT,
    'NODE_OPERATOR_REGISTRY_ADDRESSES': NODE_OPERATOR_REGISTRY_ADDRESSES,
    'STETH_ADDRESS': STETH_ADDRESS,
    'BLOCKS_BETWEEN_EXECUTION': BLOCKS_BETWEEN_EXECUTION,
    'MIN_SHARES_TO_DISTRIBUTE': MIN_SHARES_TO_DISTRIBUTE,
    'ACCOUNT': '' if ACCOUNT is None else ACCOUNT.address,
}

PRIVATE_ENV_VARS = {
    'WEB3_RPC_ENDPOINTS': WEB3_RPC_ENDPOINTS,
    'WALLET_PRIVATE_KEY': WALLET_PRIVATE_KEY,
}

assert not set(PRIVATE_ENV_VARS.keys()).intersection(set(PUBLIC_ENV_VARS.keys()))


def _mask(value):
    if isinstance(value, list):
        return [MASKED_VALUE for _ in value]
    return MASKED_VALUE if value else ''


def env_vars_for_log() -> dict:
    """All bot variables for the startup log. Secret values are masked, unset ones stay empty."""
    return {
        **PUBLIC_ENV_VARS,
        **{key: _mask(value) for key, value in PRIVATE_ENV_VARS.items()},
    }
