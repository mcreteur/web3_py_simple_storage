from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

print("Installing...")
install_solc("0.8.0")

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# compile contract
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
    solc_version="0.8.0",
)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# blockchain data
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_SERVER")))
chain_id = int(os.getenv("CHAIN_ID"))
my_address = os.getenv("MY_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")

# create the contract in Python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the transaction count
nonce = w3.eth.getTransactionCount(my_address)

# build the transaction that deploys the contract
transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)
# sign the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
print("Deploying contract...")
# send it!
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")

# increment nonce for the next transaction
nonce += 1

# working with deployed contract
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print("Initial value : " + str(simple_storage.functions.retrieve().call()))

store_transaction = simple_storage.functions.store(44).buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
print("Updating stored value...")
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
send_store_tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")

print("Here is the new value : " + str(simple_storage.functions.retrieve().call()))
