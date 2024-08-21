import requests
import json
import time
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

apikey = "7da79b34-308c-4a47-a46e-544dd6f629d0"

headers = {
    'X-CMC_PRO_API_KEY': apikey,
    'Accepts': 'application/json'
}

params = {
    'start': '1',
    'limit': '2',
    'convert': 'USD'
}

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

def fetch_and_save_data():
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        file_path = 'crypto_data.json'
        logging.info(f"Saving data to: {file_path}")
        
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
            logging.info("Data updated successfully.")
        except IOError as e:
            logging.error(f"Error writing to file: {e}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")

if __name__ == '__main__':
    while True:
        fetch_and_save_data()
        time.sleep(5)  # Sleep for 5 seconds before fetching the data again
