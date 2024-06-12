import pytest
from web3.contract.contract import ContractFunction

from contracts.node_operator_registry import RewardDistributionState
from tests.integration.contracts.contract import check_contract, check_value_type


@pytest.mark.integration
def test_node_operator_registry(web3_integration, caplog):
    check_contract(
        web3_integration.lido.node_operator_registry,
        [
            ('get_contract_version', None, lambda response: check_value_type(response, int)),
            ('get_reward_distribution_state', None, lambda response: check_value_type(response, RewardDistributionState)),
            ('distribute_reward', None, lambda response: check_value_type(response, ContractFunction)),
        ],
        caplog,
    )
