from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile Our Solidity
install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# Get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# For connecting to rinkeby
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/a25572790113470b9eeccf93a637c791")
)
chain_id = 4
my_address = "0x9F2a8825cF29D245DDDD1A251349dF9E8a50c0ef"
private_key = os.getenv("PRIVATE_KEY")

# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# 1. Build a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)

# 2. Sign the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# 3. Send the signed transaction
print("Deploying the contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")

# Working with the contract: need contract abi and contract address
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Retrieve function call - Initial value of favorite number
print(simple_storage.functions.retrieve().call())

# Store function usage transaction to store favorite number

# 1. Build the transaction
print("Updating the contract...")
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
    }
)

# 2. Sign the transaction
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

# 3. Send the signed transaction
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
store_tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")

# Retrieve function call - Value of favorite number after storing
print(simple_storage.functions.retrieve().call())
