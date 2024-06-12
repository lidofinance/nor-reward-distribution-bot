import logging
from enum import Enum

from contracts.interface import ContractInterface
from eth_typing import BlockIdentifier
from web3.contract.contract import ContractFunction

logger = logging.getLogger(__name__)


class RewardDistributionState(Enum):
    TRANSFERRED_TO_MODULE = 0
    READY_FOR_DISTRIBUTION = 1
    DISTRIBUTED = 2


class NodeOperatorRegistryContract(ContractInterface):
    abi_path = 'interfaces/NodeOperatorRegistry.json'

    def get_contract_version(self, block_identifier: BlockIdentifier = 'latest') -> int:
        result = self.functions.getContractVersion().call(block_identifier=block_identifier)
        logger.info(
            {
                'msg': 'Call `getContractVersion()`.',
                'value': result,
                'block_identifier': repr(block_identifier),
            }
        )
        return result

    def get_reward_distribution_state(self, block_identifier: BlockIdentifier = 'latest') -> RewardDistributionState:
        """
        Get the current reward distribution state.
        When status is ReadyForDistribution call `distributeReward` to distribute rewards among NOR operators.
        """
        call = self.functions.getRewardDistributionState().call(block_identifier=block_identifier)
        result = RewardDistributionState(call)
        logger.info(
            {
                'msg': 'Call `getRewardDistributionState()`.',
                'value': repr(result),
                'block_identifier': repr(block_identifier),
            }
        )
        return result

    def distribute_reward(self) -> ContractFunction:
        """
        Permissionless method for distributing all accumulated module rewards among node operators
        based on the latest accounting report.
        """
        tx = self.functions.distributeReward()
        logger.info({'msg': 'Build `distributeReward()` tx.'})
        return tx
