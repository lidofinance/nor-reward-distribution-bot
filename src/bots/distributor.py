import logging
from typing import TYPE_CHECKING

import variables
from contracts.node_operator_registry import RewardDistributionState
from metrics.metrics import REWARDS_DISTRIBUTION_STATUS, SHARES_TO_DISTRIBUTE
from web3.contract.contract import ContractFunction
from web3.exceptions import ContractLogicError
from web3.types import BlockData

if TYPE_CHECKING:
    from web3_types import Web3

logger = logging.getLogger(__name__)


class RewardLiquidationBot:
    def __init__(self, w3: 'Web3'):
        self.w3 = w3

    def execute(self, block: BlockData):
        for nor in self.w3.lido.nor_contracts:
            if nor.get_contract_version() in [1, 2]:
                logger.warning({'msg': 'Contract does not support reward distribution yet. Waiting for V3.'})
                continue

            state = nor.get_reward_distribution_state()

            REWARDS_DISTRIBUTION_STATUS.labels(nor.address).set(state.value)

            if state is not RewardDistributionState.READY_FOR_DISTRIBUTION:
                logger.info({'msg': 'NOR is not ready to distribute rewards.'})
                continue

            shares_on_balance = self.w3.lido.steth.shares_of(nor.address)

            SHARES_TO_DISTRIBUTE.labels(nor.address).set(shares_on_balance)

            if shares_on_balance < variables.MIN_SHARES_TO_DISTRIBUTE:
                logger.info({'msg': 'NOR balance is too low to distribute rewards.'})
                continue

            tx = nor.distribute_reward()
            self._send_transaction(tx)

    def _send_transaction(self, transaction: ContractFunction):
        try:
            transaction.call()
        except (ValueError, ContractLogicError) as error:
            logger.error({'msg': 'Local transaction reverted.', 'error': str(error)})
            return

        logger.info({'msg': 'Success local call. Send tx...'})

        if not variables.ACCOUNT:
            logger.warning({'msg': 'Account is not provided. Dry mode.'})
            return

        tx = transaction.build_transaction(
            {
                'from': variables.ACCOUNT.address,
                'nonce': self.w3.eth.get_transaction_count(variables.ACCOUNT.address),
            }
        )

        signed_tx = self.w3.eth.account.sign_transaction(tx, variables.ACCOUNT.key)

        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        logger.info({'msg': 'Transaction sent.', 'value': repr(tx_hash)})

        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info({'msg': 'Transaction found in blockchain.'})

        return tx_hash
