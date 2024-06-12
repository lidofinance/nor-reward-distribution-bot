from prometheus_client.metrics import Counter, Gauge, Histogram

PREFIX = 'distribution_bot'


ACCOUNT_BALANCE = Gauge('account_balance', 'Account balance', namespace=PREFIX)

REWARDS_DISTRIBUTION_STATUS = Gauge(
    'rewards_distribution_status',
    'Current smart contract distribution state.',
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
