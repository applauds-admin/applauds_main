from web3.datastructures import AttributeDict

from poap.utils.contract.abi import POAP_CONTRACT
from poap.utils.contract.web3_connection import w3, POAPTokensAddress, owner_account, chain_id

poap_contract_instance = w3.eth.contract(
    address=POAPTokensAddress, abi=POAP_CONTRACT,
)


def mint(token_id: int, recipient: str):
    nonce = w3.eth.get_transaction_count(owner_account.address)
    print(" - Nonce:", nonce)
    function_obj = poap_contract_instance.functions.mint(
        recipient,
        token_id,
        1,
        "",
    )
    estimate_gas = function_obj.estimateGas()
    print(" - Estimate GAS:", estimate_gas)

    migration_txn = function_obj.buildTransaction({
        "from": owner_account.address,
        "gas": estimate_gas,
        # "gasPrice": int(w3.eth.gas_price * 1.2),
        "nonce": nonce,
        "chainId": chain_id,
    })
    signed_txn = owner_account.sign_transaction(migration_txn)
    w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_hash = w3.toHex(w3.keccak(signed_txn.rawTransaction))
    print(" - TX hash:", tx_hash)
    tx_receipt: AttributeDict = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash, tx_receipt


def balance(token_id: int, recipient: str) -> int:
    res = poap_contract_instance.functions.balanceOf(recipient, token_id).call()
    return res
