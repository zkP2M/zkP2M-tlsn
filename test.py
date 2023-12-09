import brownie


import json
from brownie import Contract, accounts, network

def main():
    # Set up the network (development, mainnet, testnet, etc.)
    network.connect('goerli')

    # Get accounts
    sender = accounts.add('f38fc17f1de196021fad57d4f8095709f83fc4df0d3e0dd0923c1d859ec584ac')
    
    with open('abi.json', 'r') as abi_file:
        abi = json.load(abi_file)

    contract_address = "0x8374d6e81363fE432F98E46E8A6Fe0873e526FB8"

    contract = Contract.from_abi("USDCMock", contract_address, abi)

    result = contract.transfer("0x73B21642FF6A246179c8A1008AcA6FB3a7671594", "1000000", {'from': sender})
    
    # Wait for the transaction to be confirmed
    tx.wait(1)

    # Disconnect from the network
    network.disconnect()

    print(f"Sent 0.1 ether from {sender} to {receiver}")


main()
