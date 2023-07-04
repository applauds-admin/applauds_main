import hashlib

from web3.datastructures import AttributeDict

from poap.utils.contract.abi import FUNCTIONS_CONSUMER
from poap.utils.contract.web3_connection import w3, FunctionsConsumerAddress, owner_account, chain_id

functions_consumer_instance = w3.eth.contract(
    address=FunctionsConsumerAddress, abi=FUNCTIONS_CONSUMER,
)


def execute_request(request_url: str):
    """
    Call chain link functions consumer
    :param request_url: Get request to get status
           eg. https://www.example.com/course/2/verify?wallet=0xBBe5916a30751acc4E0E44bD4Fa26779f594BA11
    :return:
    """
    url_hash = hashlib.sha256(request_url.encode()).digest()
    print("url_hash:", url_hash)
    nonce = w3.eth.get_transaction_count(owner_account.address)
    print(" - Nonce:", nonce)
    function_obj = functions_consumer_instance.functions.simpleExecuteRequest(
        """const verifyAddress = args[0]

// make HTTP request
console.log(`HTTP GET Request to ${verifyAddress}`)

// construct the HTTP Request object. See: https://github.com/smartcontractkit/functions-hardhat-starter-kit#javascript-code
// params used for URL query parameters
// Example of query: https://www.example.com/course/1/verify?wallet=0x...
const request = Functions.makeHttpRequest({
  url: verifyAddress,
  params: {},
})

const response = await request
console.info(response)
// if (response.error) {
//   console.error(response.error)
//   throw Error("Request failed")
// }

const statusCode = response.status
console.info(statusCode)

// Use Functions.encodeUint256 to encode an unsigned integer to a Buffer
return Functions.encodeUint256(Math.round(statusCode))
""",
        982,
        [request_url],
        url_hash,
    )
    print(function_obj.estimate_gas())
    estimate_gas = int(function_obj.estimate_gas() * 1.5)
    print(" - Estimate GAS:", estimate_gas)
    print(" - Gas Price:", int(w3.eth.gas_price))

    execute_txn = function_obj.build_transaction({
        "from": owner_account.address,
        "gas": estimate_gas,
        # "gasPrice": int(w3.eth.gas_price * 1.2),
        "nonce": nonce,
        "chainId": chain_id,
    })
    signed_txn = owner_account.sign_transaction(execute_txn)
    w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_hash = w3.to_hex(w3.keccak(signed_txn.rawTransaction))
    print(" - TX hash:", tx_hash)
    tx_receipt: AttributeDict = w3.eth.wait_for_transaction_receipt(tx_hash)
    return url_hash, tx_hash, tx_receipt


def fetch_result(request_url: str) -> int:
    """
    Fetch request response detail
    :param request_url:
    :return:
    """
    url_hash = hashlib.sha256(request_url.encode()).digest()
    res: list[bytes] = functions_consumer_instance.functions.requestResult(url_hash).call()
    print(res)
    if res[2]:
        raise Exception("Request with error:", res[2].decode())
    return int.from_bytes(res[1], byteorder='big')
