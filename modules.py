import random
from datetime import datetime

import json
import requests
from aptos_sdk.client import RestClient

from logger import setup_gay_logger


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

def made_topaz_bid(account, collection_id):
    logger = setup_gay_logger('made_topaz_bid')

    amount = random.randint(50000, 100000)
    hours = random.randint(2, 24)

    # Current Unix timestamp in microseconds
    current_unix_timestamp = int(datetime.utcnow().timestamp() * 1e6)
    # Convert hours to microseconds and subtract one hour in microseconds (required by topaz)
    expiration_timestamp = current_unix_timestamp + ((hours - 1) * 3600 * 1e6)

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
            "0xc46dd298b89d38314b486b2182a6163c4c955dce3509bf30751c307f5ecc2f36",
            # This seems to be a placeholder value, replace with actual value as needed
            "Pontem Space Pirates"  # This seems to be a placeholder value, replace with actual value as needed
        ]
    }

print(get_verified_collection_ids())
