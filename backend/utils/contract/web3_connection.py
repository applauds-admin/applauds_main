from django.conf import settings
from eth_account.signers.base import BaseAccount
from web3 import Web3
from web3.middleware import geth_poa_middleware

# w3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"))
# BSC Testnet
# w3 = Web3(Web3.HTTPProvider("https://data-seed-prebsc-1-s1.binance.org:8545"))
# chain_id = 97
# Moonbase Alpha
# w3 = Web3(Web3.HTTPProvider("https://rpc.api.moonbase.moonbeam.network"))
# chain_id = 1287
# Mantle Testnet
# w3 = Web3(Web3.HTTPProvider("https://rpc.testnet.mantle.xyz"))
# chain_id = 5001
# Mumbai
w3 = Web3(Web3.HTTPProvider("https://rpc-mumbai.maticvigil.com"))
chain_id = 80001
# Support poa chain
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

private_key = settings.WALLET_PK
owner_account: BaseAccount = w3.eth.account.from_key(private_key)
w3.eth.default_account = owner_account.address

# BSC / MoonBase
# POAPTokensAddress = "0xb9001d778F7000E8d32D90d170DF2246b1c89c76"
# Mumbai
POAPTokensAddress = "0xe40E5a43C7c6659ec886D691D757F26f2A0AA776"
FunctionsConsumerAddress = "0x976BE2768B5F1693E29b4cc7961b418C9D0B2D3c"

# attitude margin bread glass cat derive pen venue battle pioneer cable taxi
