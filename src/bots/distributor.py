import logging
from typing import TYPE_CHECKING

from web3.contract.contract import ContractFunction
from web3.exceptions import ContractLogicError

import variables
from contracts.node_operator_registry import RewardDistributionState
from metrics.metrics import REWARDS_DISTRIBUTION_STATUS
from web3.types import BlockData, TxParams, Wei

if TYPE_CHECKING:
    from web3_types import Web3

logger = logging.getLogger(__name__)


class RewardLiquidationBot:
    def __init__(self, w3: 'Web3'):
        self.w3 = w3

    def execute(self, block: BlockData):
        if self.w3.lido.node_operator_registry.get_contract_version() in [1, 2]:
            logger.warning({'msg': 'Contract does not support reward distribution yet. Waiting for V3.'})
            return

        state = self.w3.lido.node_operator_registry.get_reward_distribution_state()

        REWARDS_DISTRIBUTION_STATUS.set(state.value)

        if state is not RewardDistributionState.READY_FOR_DISTRIBUTION:
            logger.info({'msg': 'NOR is not ready to distribute rewards.'})
            return

        tx = self.w3.lido.node_operator_registry.distribute_reward()

        if not variables.ACCOUNT:
            logger.warning({'msg': 'Account is not provided. Dry mode.'})
            return

        return self._send_transaction(tx)

    def _send_transaction(self, transaction: ContractFunction):
        try:
            transaction.call()
        except (ValueError, ContractLogicError) as error:
            logger.error({'msg': 'Local transaction reverted.', 'error': str(error)})
            return

        logger.info({'msg': 'Success local call. Send tx...'})

        tx = transaction.build_transaction({
            "from": variables.ACCOUNT.address,
            "nonce": self.w3.eth.get_transaction_count(variables.ACCOUNT.address),
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, variables.ACCOUNT.key)

        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        logger.info({'msg': 'Transaction sent.', 'value': tx_hash})

        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info({'msg': 'Transaction found in blockchain.'})

        return tx_hash
