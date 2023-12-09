import json
from brownie import Contract, accounts, network
import os

CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
VERIFIER_PRIVATE_KEY = os.environ.get('VERIFIER_PRIVATE_KEY')
NETWORK = os.env('NETWORK')

def call_onramp(intentHash, blockTimestamp, amount, receiver):

    network.connect(NETWORK)

    with open('contract_abi.json', 'r') as abi_file:
        abi = json.load(abi_file)

    verifier_eoa = accounts.add(VERIFIER_PRIVATE_KEY)
    contract = Contract.from_abi("Ramp", CONTRACT_ADDRESS, abi)

    tx = contract.onRampWithoutProof(
        intentHash,
        amount,
        blockTimestamp,
        receiver, 
        {'from': verifier_eoa}
    )

    # Wait for the transaction to be confirmed
    tx.wait(1)

    # Disconnect from the network
    network.disconnect()

    print(f"Completed onramp")