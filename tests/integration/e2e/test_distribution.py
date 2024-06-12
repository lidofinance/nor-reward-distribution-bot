import pytest
from web3.types import BlockData

import variables
from bots.distributor import RewardLiquidationBot
from contracts.node_operator_registry import RewardDistributionState


@pytest.mark.integration
@pytest.mark.parametrize(
    'web3_integration',
    [1716865],
    indirect=True,
)
def test_happy_path_distribution(web3_integration, set_account):
    web3_integration.provider.make_request('anvil_setBalance', [variables.ACCOUNT.address, '0x500000000000000000000000'])

    rlb = RewardLiquidationBot(web3_integration)

    assert web3_integration.lido.node_operator_registry.get_reward_distribution_state() == RewardDistributionState.READY_FOR_DISTRIBUTION

    tx_hash = rlb.execute(BlockData())

    assert web3_integration.lido.node_operator_registry.get_reward_distribution_state() == RewardDistributionState.DISTRIBUTED

    assert web3_integration.eth.get_transaction_receipt(tx_hash)
