import logging

from contracts.interface import ContractInterface
from eth_typing import BlockIdentifier, ChecksumAddress

logger = logging.getLogger(__name__)



class StETHContract(ContractInterface):
    abi_path = 'interfaces/StETH.json'

    def shares_of(self, address: ChecksumAddress, block_identifier: BlockIdentifier = 'latest') -> int:
        """
        Get the number of shares held by a specific address.
        """
        result = self.functions.sharesOf(address).call(block_identifier=block_identifier)
        logger.info(
            {
                'msg': f'Call `sharesOf({address})`.',
                'value': repr(result),
                'block_identifier': repr(block_identifier),
            }
        )
        return result
