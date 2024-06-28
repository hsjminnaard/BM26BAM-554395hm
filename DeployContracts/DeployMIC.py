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

# Write the compiled contract to a file
with open("compiled_code_MIC.json", "w") as file:
    json.dump(compiled_sol_MIC, file)

# Get the bytecode
bytecode = compiled_sol_MIC["contracts"]["MicroInvestingContract.sol"]["MicroInvestingContract"]["evm"]["bytecode"]["object"]

# Get the ABI
abi = compiled_sol_MIC["contracts"]["MicroInvestingContract.sol"]["MicroInvestingContract"]["abi"]

# For connecting to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_address = "0x3965E1BB2B1281eF3968D5e2CA97e5e3F07B7AbC"
private_key = "0x8f835efe66fb5d297c5cc7e98ee9c78bf51aa6a946fa66dc7a897e1f92da583c"

# Create the contract in Python
MicroInvestingContract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get latest transaction
nonce = w3.eth.get_transaction_count(my_address)

# Prompt the user for the contract name and total supply
contract_name = input("Enter the contract name: ")
total_supply = int(input("Enter the total supply: "))

# 1. Build a transaction
transaction = MicroInvestingContract.constructor(contract_name, total_supply).build_transaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce
    }
)

# 2. Sign the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# 3. Send the signed transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("MicroInvestingContract Deployed!")

# Now you can interact with the contract using its ABI and address.
contract_address = tx_receipt.contractAddress
micro_investing_contract = w3.eth.contract(address=contract_address, abi=abi)

# Example interaction: Listing a bond for sale
token_id = 1
price = w3.to_wei(1, 'ether')
list_tx = micro_investing_contract.functions.listBondForSale(token_id, price).build_transaction({
    'chainId': chain_id,
    'gasPrice': w3.eth.gas_price,
    'from': my_address,
    'nonce': nonce + 1
})
signed_list_tx = w3.eth.account.sign_transaction(list_tx, private_key=private_key)
w3.eth.send_raw_transaction(signed_list_tx.rawTransaction)
print("Bond listed for sale!")

# Example interaction: Buying a bond
buyer_address = "0x88e8223db67A75a4c1384Ada292696dCDfC1d619" 
buyer_private_key = "0xbc28da3dc578cd12cc48be302c264fd29c9e0848d79da1c869b43dd9ce643ff8"  
nonce = w3.eth.get_transaction_count(buyer_address)
buy_tx = micro_investing_contract.functions.buyBond(token_id).build_transaction({
    'chainId': chain_id,
    'gasPrice': w3.eth.gas_price,
    'from': buyer_address,
    'nonce': nonce,
    'value': price
})
signed_buy_tx = w3.eth.account.sign_transaction(buy_tx, private_key=buyer_private_key)
w3.eth.send_raw_transaction(signed_buy_tx.rawTransaction)
print("Bond purchased!")
