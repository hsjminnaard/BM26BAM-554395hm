from solcx import compile_standard, install_solc
import json
from web3 import Web3

# Read the compiled contract from JSON
with open("compiled_code_SC.json", "r") as file:
    compiled_sol_SC = json.load(file)

# Get the bytecode and ABI
bytecode = compiled_sol_SC["contracts"]["SubscriptionContract.sol"]["SubscriptionContract"]["evm"]["bytecode"]["object"]
abi = compiled_sol_SC["contracts"]["SubscriptionContract.sol"]["SubscriptionContract"]["abi"]

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_address = "0x3965E1BB2B1281eF3968D5e2CA97e5e3F07B7AbC"
private_key = "0x8f835efe66fb5d297c5cc7e98ee9c78bf51aa6a946fa66dc7a897e1f92da583c"

# Example of a correct deployed contract address
deployed_contract_address = "0xa7CBa5d3fbDA5d7226B27838188C2A3a71260157"

# Load contract instance using the deployed address
contract = w3.eth.contract(address=deployed_contract_address, abi=abi)

# Example: Paying the subscription fee
def pay_subscription_fee():
    amount_to_pay = 10 * 10**18  # 10 ether in wei
    nonce = w3.eth.get_transaction_count(my_address)

    # Build transaction
    transaction = contract.functions.paySubscriptionFee().build_transaction({
        'chainId': chain_id,
        'gasPrice': w3.eth.gas_price,
        'from': my_address,
        'nonce': nonce,
        'value': amount_to_pay
    })

    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Subscription fee paid successfully by {my_address}. Transaction receipt: {tx_receipt}")

# Example usage
pay_subscription_fee()
