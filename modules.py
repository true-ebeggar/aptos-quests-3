import random
import time
from datetime import datetime

import json
import requests
from aptos_sdk.client import ClientConfig
from aptos_sdk.client import RestClient

from logger import setup_gay_logger

Z8 = 10**8
Z6 = 10**6

ClientConfig.max_gas_amount = 100_00
# This adjustment decreases the required balance for transaction execution.
# It changes the upper limit for gas, avoiding trigger safety shut down.

Rest_Client = RestClient("https://fullnode.mainnet.aptoslabs.com/v1")

def submit_and_log_transaction(account, payload, logger):
    try:
        txn = Rest_Client.submit_transaction(account, payload)
        Rest_Client.wait_for_transaction(txn)
        logger.info(f'Success: https://explorer.aptoslabs.com/txn/{txn}?network=mainnet')
    except AssertionError as e:
        logger.error(f"AssertionError caught: {e}")
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")


def get_verified_collection_ids():
    url = 'https://api-v1.topaz.so/api/explore-collections?from=0&to=100'

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'If-None-Match': 'W/"3806-nRMIXo8sly6GTHX/2VkJfr6aKGo"',
        'Origin': 'https://www.topaz.so',
        'Referer': 'https://www.topaz.so/',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Opera";v="106"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0'
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    verified_collection_ids = {item['collection_id'] for item in data['data'] if item['verified']}
    return verified_collection_ids

def made_topaz_bid(account, contract: str, name: str):
    logger = setup_gay_logger('made_topaz_bid')

    amount = random.randint(50, 100)
    amount_str = str(amount) + '000'
    amount = int(amount_str)
    hours = random.randint(2, 24)

    # Current Unix timestamp in microseconds
    current_unix_timestamp = int(datetime.utcnow().timestamp() * 1e6)
    # Convert hours to microseconds and subtract one hour in microseconds (required by topaz)
    expiration_timestamp = int(current_unix_timestamp + ((hours - 1) * 3600 * 1e6))

    payload = {
        "type": "entry_function_payload",
        "function": "0x2c7bccf7b31baf770fdbcc768d9e9cb3d87805e255355df5db32ac9a669010a2::collection_marketplace::bid",
        "type_arguments": [
            "0x1::aptos_coin::AptosCoin"
        ],
        "arguments": [
            str(amount),
            "1",
            str(expiration_timestamp),
            contract,
            name,
        ]
    }

    submit_and_log_transaction(account, payload, logger)
    logger.info(f"offer value: {amount / Z8} | offer duration: {hours}h. ")

def get_available_free_mints():

    url = 'https://api.wapal.io/api/collection/editions?page=1&limit=20&edition=open-edition&isApproved=true'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://launchpad.wapal.io',
        'Referer': 'https://launchpad.wapal.io/',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Opera";v="106"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0'
    }

    response = requests.get(url, headers=headers)
    response_json = response.json()

    # Filter collections
    available_collections = []
    for item in response_json['data']:
        if not item['status']['sold_out'] and item['candyMachine']['public_sale_price'] == 0 and item['candyMachine']['whitelist_price'] == 0:
            collection_format = f"{item['candyMachine']['resource_account']}::{item['name']}"
            available_collections.append(collection_format)

    return available_collections

def mint_free_mint(account, contract: str):
    logger = setup_gay_logger('mint_free_mint')

    payload = {
        "type": "entry_function_payload",
        "function": "0x6547d9f1d481fdc21cd38c730c07974f2f61adb7063e76f9d9522ab91f090dac::candymachine::mint_script",
        "type_arguments": [],
        "arguments": [
            contract
        ]
    }

    submit_and_log_transaction(account, payload, logger)