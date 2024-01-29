import requests

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

def delete_line_from_file(filename, line_to_delete):
    with open(filename, 'r') as file:
        lines = file.readlines()

    with open(filename, 'w') as file:
        for line in lines:
            if line.strip("\n") != line_to_delete:
                file.write(line)