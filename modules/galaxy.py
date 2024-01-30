import json
import random
from time import time
from datetime import datetime, timedelta
import string

import nltk
from nltk.corpus import words
import requests

from aptos_sdk.account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from logger import setup_gay_logger
from utils import create_headers

nltk.download('words', quiet=True)
word_list = words.words()
w3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))
galaxy_query = 'https://graphigo.prd.galaxy.eco/query'


def update_user_address(account_apt, account_evm, galaxy_token: str):
    logger = setup_gay_logger("update_user_address")
    try:

        headers = create_headers(galaxy_token)

        current_time = int(time())
        rounded_time = int(current_time - (current_time % 3600))
        apt_address = account_apt.address()

        message = (f"You are updating your Galaxy profile with aptos address APTOS:{apt_address}"
                   f"Please sign the transaction to confirm.")

        full_message = f'APTOS\nmessage: {message}\nnonce: {time}'
        signature = account_apt.sign(full_message.encode('utf-8'))

        payload = {
            "operationName": "UpdateUserAddress",
            "variables": {
                "input": {
                    "address": str(account_evm.address),
                    "addressType": "EVM",
                    "updateAddress": str(apt_address),
                    "updateAddressType": "APTOS",
                    "sig": str(signature.signature.hex()),
                    "sigNonce": str(rounded_time),
                    "addressPublicKey": str(account_apt.public_key())
                }
            },
            "query": "mutation UpdateUserAddress($input: UpdateUserAddressInput!) {\n  updateUserAddress(input: $input) {\n    code\n    message\n    __typename\n  }\n}\n"
        }

        # Send the POST request
        response = requests.post(galaxy_query, headers=headers, json=payload)

        if response.status_code == 200:
            response_json = response.json()
            if 'data' in response_json and response_json['data'].get('updateUserAddress') is None:
                logger.info("Address bind successful.")
                return True
            else:
                logger.warning("Address bind returned non-null or no data field present.")
                return None
        else:
            logger.error(f"Update user address request failed."
                         f"\nStatus code {response.status_code}"
                         f"\nResponse {response.text}")
            return None
    except Exception as e:
        logger.critical(f"Exception during the update user address request: "
                        f"\n{e}")
        return None


def sign_in_evm(account_evm):
    logger = setup_gay_logger('sign_in_evm')
    try:
        characters = string.ascii_letters + string.digits
        nonce = ''.join(random.choice(characters) for i in range(17))
        current_time = datetime.utcnow()
        seven_days_later = current_time + timedelta(days=7)
        issued_time = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        expiration_time = seven_days_later.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        message = (f"galxe.com wants you to sign in with your Ethereum account:\n"
                   f"{account_evm.address}\n\n"
                   f"Sign in with Ethereum to the app.\n\n"
                   f"URI: https://galxe.com\n"
                   f"Version: 1\n"
                   f"Chain ID: 1\n"
                   f"Nonce: {nonce}\n"
                   f"Issued At: {issued_time}\n"
                   f"Expiration Time: {expiration_time}")

        signature = account_evm.sign_message(encode_defunct(text=message))

        data = {
            "operationName": "SignIn",
            "variables": {
                "input": {
                    "address": account_evm.address,
                    "message": message,
                    "signature": signature.signature.hex(),
                    "addressType": "EVM"
                }
            },
            "query": "mutation SignIn($input: Auth) {\n  signin(input: $input)\n}\n"
        }

        response = requests.post(galaxy_query, json=data)

        if response.status_code == 200 and 'signin' in response.text:
            signin = response.json()['data']['signin']
            logger.info('Got the signIn token')
            return signin
        else:
            logger.error(f"{account_evm.address} Login failed."
                         f"\nResponse code: {response.status_code}."
                         f"\nResponse content {response.content}")
            return None

    except Exception as e:
        logger.critical(f"{account_evm.address} Login failed."
                        f"\nException: {e}")
        return None


def sign_in_apt(account_apt):
    logger = setup_gay_logger('sign_in_apt')
    apt_address = account_apt.address()
    public_key = account_apt.public_key()

    try:
        now = datetime.utcnow()
        next_day = now + timedelta(days=7)
        iso_time_next_day = next_day.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        current_time = int(time())
        rounded_time = int(current_time - (current_time % 3600))

        message = (f"Galxe.com wants you to sign in with your Aptos account: "
                   f"{apt_address}; "
                   f"<Public key: {public_key}>, "
                   f"<Version: 1>, "
                   f"<Chain ID: 1>, "
                   f"<Nonce: {rounded_time}>, "
                   f"<Expiration Time: {iso_time_next_day}>")

        full_message = f'APTOS\nmessage: {message}\nnonce: {rounded_time}'

        signature = account_apt.sign(full_message.encode('utf-8'))

        data = {
            "operationName": "SignIn",
            "variables": {
                "input": {
                    "address": str(apt_address),
                    "message": message,
                    "signature": str(signature.signature.hex())
                }
            },
            "query": "mutation SignIn($input: Auth) {\n  signin(input: $input)\n}\n"
        }

        response = requests.post(galaxy_query, json=data)

        if response.status_code == 200 and 'signin' in response.text:
            signin = response.json()['data']['signin']
            logger.info('Got the signIn token')
            return signin
        else:
            logger.error(f"{apt_address.address} Login failed."
                         f"\nResponse code: {response.status_code}."
                         f"\nResponse content {response.content}")
            return None

    except Exception as e:
        logger.critical(f"{apt_address.address} Login failed."
                        f"\nException: {e}")
        return None

def create_username(galaxy_token: str, username: str, address: str):
    logger = setup_gay_logger('create_username')
    try:
        headers = create_headers(galaxy_token)

        payload = {
            "operationName": "CreateNewAccount",
            "query": "mutation CreateNewAccount($input: CreateNewAccount!) {\n  createNewAccount(input: $input)\n}\n",
            "variables": {
                "input": {
                    "schema": f"EVM:{address}",
                    "socialUsername": "",
                    "username": username
                }
            }
        }

        response = requests.post(galaxy_query, headers=headers, json=payload)
        response_json = response.json()

        if 'data' in response_json and 'createNewAccount' in response_json['data']:
            logger.info(f"Account creation successful for username: {username}")
            return True
        else:
            logger.error(f"Account creation failed for username: {username}."
                         f"\nResponse: {response.text}")
            return False

    except Exception as e:
        logger.error(f"Exception during account creation for username: {username}. "
                     f"\nException: {e}")
        return False


def check_username_availability(galaxy_token: str, username: str):
    try:
        headers = create_headers(galaxy_token)

        payload = {
            "operationName": "IsUsernameExisting",
            "query": "query IsUsernameExisting($username: String!) {\n  usernameExist(username: $username)\n}\n",
            "variables": {
                "username": username
            }
        }

        response = requests.post(galaxy_query, headers=headers, json=payload)
        response_json = response.json()
        is_username_existing = response_json.get('data', {}).get('usernameExist', None)
        return is_username_existing
    except Exception:
        return None


def get_basic_user_info(galaxy_token: str, user_address: str):
    logger = setup_gay_logger('get_basic_user_info')

    try:
        headers = create_headers(galaxy_token)

        payload = {
            "operationName": "BasicUserInfo",
            "variables": {"address": user_address},
            "query": """query BasicUserInfo($address: String!) {
                        addressInfo(address: $address) {
                            id
                            username
                            address
                            aptosAddress
                            hasEvmAddress
                            hasAptosAddress
                            hasTwitter
                            twitterUserID
                            twitterUserName
                        }
                    }"""
        }

        response = requests.post(galaxy_query, headers=headers, json=payload)
        print(json.dumps(response.json(), indent=4))

        if response.status_code == 200:
            user_info = response.json().get('data', {}).get('addressInfo', {})
            logger.info(f"User info retrieval successful")
            return user_info
        else:
            logger.error(f"Failed to retrieve user info for address: {user_address}."
                         f"\nResponse: {response.text}")
            return None

    except Exception as e:
        logger.critical(f"Exception during user info retrieval for address: {user_address}."
                        f"\nException: {e}")
        return None

def create_new_account(galaxy_token: str, address_evm):
    logger = setup_gay_logger('create_new_account')
    while True:
        username = random.choice(word_list)
        if check_username_availability(galaxy_token, username) is False:
            create_username(galaxy_token, username, address_evm)
            get_basic_user_info(galaxy_token, address_evm)
            break
        logger.error(f"{username} username is already taken. Retry...")





token = sign_in_evm(account_evm)
create_new_account(token, account_evm.address)
update_user_address(account_apt, account_evm, token)
get_basic_user_info(token, account_evm.address)