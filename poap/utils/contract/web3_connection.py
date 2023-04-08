from eth_account.signers.base import BaseAccount
from web3 import Web3
from web3.middleware import geth_poa_middleware

# w3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"))
w3 = Web3(Web3.HTTPProvider("https://data-seed-prebsc-2-s3.binance.org:8545"))
chain_id = 97
# chain_id = 5
# Support bsc poa chain
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

private_key = "0xafcc63e97b127f1955999335bab67d6ae88ee2afab8d408aac601f12c24c51d1"
owner_account: BaseAccount = w3.eth.account.from_key(private_key)
w3.eth.default_account = owner_account.address

POAPTokensAddress = "0xb9001d778F7000E8d32D90d170DF2246b1c89c76"
