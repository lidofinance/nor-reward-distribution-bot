import logging
from typing import cast

import variables
from contracts.node_operator_registry import NodeOperatorRegistryContract
from web3 import Web3
from web3.module import Module

logger = logging.getLogger(__name__)


class LidoContracts(Module):
    def __init__(self, w3: Web3):
        super().__init__(w3)
        self._load_contracts()

    def _load_contracts(self):
        self.node_operator_registry = cast(
            NodeOperatorRegistryContract,
            self.w3.eth.contract(
                address=self.w3.to_checksum_address(variables.NODE_OPERATOR_REGISTRY_ADDRESS),
                ContractFactoryClass=NodeOperatorRegistryContract,
            ),
        )
