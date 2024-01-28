import random
import time

from aptos_sdk.client import ClientConfig
from aptos_sdk.account import Account
from logger import setup_gay_logger
from modules import Rest_Client, get_verified_collection_ids, made_topaz_bid

MIN_SLEEP = 120
MAX_SLEEP = 160
Z8 = 10**8
Z6 = 10**6

config = ClientConfig()
config.max_gas_amount = 100_00
# This adjustment decreases the required balance for transaction execution.
# It changes the upper limit for gas, avoiding trigger safety shut down.

def process_key(key):
    account = Account.load_key(key)
    address = account.address()

    logger = setup_gay_logger(f"{address}")
    verified_collection_ids = get_verified_collection_ids()

    chosen_collection = random.choice(list(verified_collection_ids))
    contract, name = chosen_collection.split("::")
    logger.info(f'making a bid on {name}')
    if made_topaz_bid(account, contract, name):
        return 0


def delete_line_from_file(filename, line_to_delete):
    with open(filename, 'r') as file:
        lines = file.readlines()

    with open(filename, 'w') as file:
        for line in lines:
            if line.strip("\n") != line_to_delete:
                file.write(line)

# Main logic
with open('pkey.txt', 'r') as file:
    pkeys = file.readlines()

for pkey in pkeys:
    pkey = pkey.strip()
    result = process_key(pkey)
    if result == 0:
        delete_line_from_file('pkey.txt', pkey)
    time.sleep(random.randint(MIN_SLEEP, MAX_SLEEP))