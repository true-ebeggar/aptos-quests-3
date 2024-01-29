import random
import time

from aptos_sdk.client import ClientConfig
from aptos_sdk.account import Account
from logger import setup_gay_logger
from modules import made_topaz_bid, mint_free_nft
from utils import (
    get_verified_collection_ids,
    get_available_free_mints,
    delete_line_from_file)

MIN_SLEEP = 120
MAX_SLEEP = 160
Z8 = 10**8
Z6 = 10**6

config = ClientConfig()
config.max_gas_amount = 100_00
# This adjustment decreases the required balance for transaction execution.
# It changes the upper limit for gas, avoiding triggering tx termination.

def process_key(key):
    # Load the account using the provided key
    account = Account.load_key(key)
    address = account.address()

    logger = setup_gay_logger(f"Acc | {address}")
    logger.info(f"Processing started")

    # Fetch verified collection IDs
    verified_collection_ids = get_verified_collection_ids()
    logger.info("Retrieved verified collection IDs")

    # Choose a collection for bidding
    chosen_collection_for_bid = random.choice(list(verified_collection_ids))
    contract, name = chosen_collection_for_bid.split("::")
    logger.info(f"Chosen collection for bid: {name}")

    # Make a bid
    bid = made_topaz_bid(account, contract, name)
    if bid == 1:
        return 1

    # Retrieve available free mints (currently out of use due to wapal.io page lags)
    # free_mints = get_available_free_mints()
    free_mints = [
        '0x7c8802abae072d0903b3fc6c5e1a7b34aa99ad9e323f3beb65cbd44a6fc869d5::2 THE MOON',
        '0xa79267255727285e55bc42d34134ffa2133b6983391846810d39f094fb5f1c87::Make Every M🌐ve Count.']

    # logger.info("Retrieved list of available free mints")

    # Choose a free mint
    chosen_free_mint = random.choice(list(free_mints))
    contract1, name1 = chosen_free_mint.split("::")
    logger.info(f"Chosen free mint collection: {name1}")

    # Mint the chosen free mint
    mint = mint_free_nft(account, contract1)
    if mint == 1:
        return 1

    logger.info("Processing completed for account")
    return 0

# Main logic
with open('pkey.txt', 'r') as file:
    pkeys = file.readlines()

for pkey in pkeys:
    pkey = pkey.strip()
    try:
        result = process_key(pkey)
        if result == 0:
            delete_line_from_file('pkey.txt', pkey)
    except Exception:
        continue
    time.sleep(random.randint(MIN_SLEEP, MAX_SLEEP))