import logging
from unittest.mock import Mock

import pytest
from bots.distributor import RewardLiquidationBot
from contracts.node_operator_registry import RewardDistributionState
from web3.types import BlockData

pytestmark = pytest.mark.unit


@pytest.fixture
def distributor(web3_unit):
    yield RewardLiquidationBot(web3_unit)


def test_unsupported_contract_version(distributor, caplog):
    distributor.w3.lido.node_operator_registry.get_contract_version = Mock(return_value=2)
    distributor.w3.lido.node_operator_registry.get_reward_distribution_state = Mock()
    distributor._send_transaction = Mock()

    distributor.execute(BlockData())

    assert 'Contract does not support reward distribution yet. Waiting for V3.' in caplog.messages[0]
    distributor.w3.lido.node_operator_registry.get_reward_distribution_state.assert_not_called()
    distributor._send_transaction.assert_not_called()


def test_contract_not_ready_to_distribute(distributor, caplog):
    caplog.set_level(logging.INFO)

    distributor.w3.lido.node_operator_registry.get_contract_version = Mock(return_value=3)
    distributor._send_transaction = Mock()

    distributor.w3.lido.node_operator_registry.get_reward_distribution_state = Mock(
        return_value=RewardDistributionState.TRANSFERRED_TO_MODULE,
    )
    distributor.execute(BlockData())
    assert 'NOR is not ready to distribute rewards.' in caplog.messages[0]

    distributor.w3.lido.node_operator_registry.get_reward_distribution_state = Mock(return_value=RewardDistributionState.DISTRIBUTED)
    distributor.execute(BlockData())
    assert 'NOR is not ready to distribute rewards.' in caplog.messages[1]

    distributor._send_transaction.assert_not_called()


def test_dry_mode(distributor, caplog):
    distributor._send_transaction(Mock())

    assert 'Account is not provided. Dry mode.' in caplog.messages[0]


def test_execute(distributor, set_account):
    distributor._send_transaction = Mock()

    distributor.w3.lido.node_operator_registry.get_contract_version = Mock(return_value=3)
    distributor.w3.lido.node_operator_registry.get_reward_distribution_state = Mock(
        return_value=RewardDistributionState.READY_FOR_DISTRIBUTION,
    )

    distributor.execute(BlockData())

    distributor._send_transaction.assert_called_once()
    distributor.w3.lido.node_operator_registry.distribute_reward.assert_called_once()
