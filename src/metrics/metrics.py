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

SHARES_TO_DISTRIBUTE = Gauge(
    'shares_to_distribute',
    'Current shares to distribute among node operators.',
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

INFO = Info(name='build', documentation='Info metric', namespace=PREFIX)
CONVERTED_PUBLIC_ENV = {k: str(v) for k, v in PUBLIC_ENV_VARS.items()}
INFO.info(CONVERTED_PUBLIC_ENV)
