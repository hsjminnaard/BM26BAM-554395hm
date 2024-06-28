from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os

# Connect to the Ethereum node (Ganache, for example)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# Address and private key of the account deploying and interacting with the contract
my_address = "0x3965E1BB2B1281eF3968D5e2CA97e5e3F07B7AbC"
private_key = "0x8f835efe66fb5d297c5cc7e98ee9c78bf51aa6a946fa66dc7a897e1f92da583c"

# Read the compiled contract code
with open("compiled_code_BIC.json", "r") as file:
    compiled_sol_BIC = json.load(file)

# Get the bytecode and ABI from the compiled contract
bytecode = compiled_sol_BIC["contracts"]["BondIssuanceContract.sol"]["BondIssuanceContract"]["evm"]["bytecode"]["object"]
abi = compiled_sol_BIC["contracts"]["BondIssuanceContract.sol"]["BondIssuanceContract"]["abi"]

# Create a contract object
BondIssuanceContract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Deploy the contract
nonce = w3.eth.get_transaction_count(my_address)
chain_id = 1337  # Update with your chain ID
third_party_verifier_address = my_address  # Assuming verifier is the same account for simplicity

transaction = BondIssuanceContract.constructor(third_party_verifier_address).build_transaction({
    'chainId': chain_id,
    'gas': 2000000,
    'gasPrice': w3.eth.gas_price,
    'from': my_address,
    'nonce': nonce,
})

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"BondIssuanceContract deployed at {tx_receipt.contractAddress}")

# Interact with the deployed contract
contract_address = tx_receipt.contractAddress
contract = w3.eth.contract(address=contract_address, abi=abi)

# Verify the user (in this case, the same user issuing the bond)
verify_user_txn = contract.functions.verifyUser(my_address, True).build_transaction({
    'chainId': chain_id,
    'gas': 200000,
    'gasPrice': w3.eth.gas_price,
    'from': my_address,
    'nonce': nonce + 1,
})

signed_verify_user_txn = w3.eth.account.sign_transaction(verify_user_txn, private_key=private_key)
tx_verify_user_hash = w3.eth.send_raw_transaction(signed_verify_user_txn.rawTransaction)
tx_verify_user_receipt = w3.eth.wait_for_transaction_receipt(tx_verify_user_hash)
print(f"User verified: {tx_verify_user_receipt.status}")

# Issue a bond
bond_name = "Sample Bond"
total_supply = 1000
price_per_bond = w3.to_wei(0.01, 'ether')

issue_bond_txn = contract.functions.issueBond(bond_name, total_supply, price_per_bond).build_transaction({
    'chainId': chain_id,
    'gas': 200000,
    'gasPrice': w3.eth.gas_price,
    'from': my_address,
    'nonce': nonce + 2,
})

signed_issue_bond_txn = w3.eth.account.sign_transaction(issue_bond_txn, private_key=private_key)
tx_issue_bond_hash = w3.eth.send_raw_transaction(signed_issue_bond_txn.rawTransaction)
tx_issue_bond_receipt = w3.eth.wait_for_transaction_receipt(tx_issue_bond_hash)
print(f"Bond issued: {tx_issue_bond_receipt.status}")

