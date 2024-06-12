from contracts.extention import LidoContracts
from web3 import Web3 as _Web3


class Web3(_Web3):
    lido: LidoContracts
