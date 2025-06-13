from prometheus_client.metrics import Counter, Gauge, Histogram, Info
from variables import PUBLIC_ENV_VARS

PREFIX = 'distribution_bot'

ACCOUNT_BALANCE = Gauge('account_balance', 'Account balance', ['address'], namespace=PREFIX)

REWARDS_DISTRIBUTION_STATUS = Gauge(
    'rewards_distribution_status',
    'Current smart contract distribution state.',
    ['address'],
    namespace=PREFIX,
)

LATEST_BLOCK_NUMBER = Gauge('latest_block_number', 'Latest checked block number.', namespace=PREFIX)

UNEXPECTED_EXCEPTIONS = Counter(
    'unexpected_exceptions',
    'Total count of unexpected exceptions',
    ['type'],
    namespace=PREFIX,
)

ETH_RPC_REQUESTS_DURATION = Histogram(
    'eth_rpc_requests_duration',
    'Duration of requests to ETH1 RPC',
    namespace=PREFIX,
)
ETH_RPC_REQUESTS = Counter(
    'eth_rpc_requests',
    'Total count of requests to ETH1 RPC',
    ['method', 'code', 'domain'],
    namespace=PREFIX,
)

INFO = Info(name='build', documentation='Info metric', namespace=PREFIX)
CONVERTED_PUBLIC_ENV = {k: str(v) for k, v in PUBLIC_ENV_VARS.items()}
INFO.info(CONVERTED_PUBLIC_ENV)
