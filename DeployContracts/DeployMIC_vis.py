from solcx import compile_standard, install_solc
import json
from web3 import Web3

# Read the Solidity contract
with open("./Contracts/MicroInvestingContract.sol", "r") as file:
    MicroInvestingContract_file = file.read()

# Install specific Solidity compiler version
install_solc("0.6.0")

# Compile the Solidity contract
compiled_sol_MIC = compile_standard(
    {
        "language": "Solidity",
        "sources": {"MicroInvestingContract.sol": {"content": MicroInvestingContract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0"
)

# Get the bytecode
bytecode = compiled_sol_MIC["contracts"]["MicroInvestingContract.sol"]["MicroInvestingContract"]["evm"]["bytecode"]["object"]

# Get the ABI
abi = compiled_sol_MIC["contracts"]["MicroInvestingContract.sol"]["MicroInvestingContract"]["abi"]

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_address = "0x3965E1BB2B1281eF3968D5e2CA97e5e3F07B7AbC"
private_key = "0x8f835efe66fb5d297c5cc7e98ee9c78bf51aa6a946fa66dc7a897e1f92da583c"

# Deploy the contract
MicroInvestingContract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get latest transaction nonce
nonce = w3.eth.get_transaction_count(my_address)

# Deploy the contract
transaction = MicroInvestingContract.constructor("SimpleToken", 1000).build_transaction({
    'chainId': chain_id,
    'gasPrice': w3.eth.gas_price,
    'from': my_address,
    'nonce': nonce,
})

# Sign the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# Send the transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Contract deployed!")
contract_address = tx_receipt.contractAddress

# Instantiate the contract
micro_investing_contract = w3.eth.contract(address=contract_address, abi=abi)

# Transfer example
receiver_address = "0x08F6ff912E3083C2bCf40dE69bBE76AB355c3213"
amount = 100

# Get the latest nonce
nonce = w3.eth.get_transaction_count(my_address)

# Build the transaction
transfer_tx = micro_investing_contract.functions.transfer(receiver_address, amount).build_transaction({
    'chainId': chain_id,
    'gasPrice': w3.eth.gas_price,
    'from': my_address,
    'nonce': nonce,
})

# Sign the transaction
signed_transfer_tx = w3.eth.account.sign_transaction(transfer_tx, private_key=private_key)

# Send the transaction
tx_hash = w3.eth.send_raw_transaction(signed_transfer_tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f"{amount} tokens transferred from {my_address} to {receiver_address}")
