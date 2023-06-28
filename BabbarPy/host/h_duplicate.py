"""
MIT License

Copyright (c) 2023 BabbarTech

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import configparser
import csv
import requests
import os
import time
import sys

def get_api_key():
    config = configparser.ConfigParser()
    # Check if the 'config.ini' file does not exist or cannot be read,
    # or if the 'API' section or 'api_key' key are not present in the config
    if not os.path.exists('config.ini') or not config.read('config.ini') or not 'API' in config or not 'api_key' in config['API']:
        # Prompt the user to enter their API key
        api_key = input("Entrez votre clé API: ")
        # Update the 'config' object with the API key
        config['API'] = {'api_key': api_key}
        # Write the updated config object to the 'config.ini' file
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        # Return the API key
        return api_key
    else:
        # If the 'config.ini' file exists and contains the API key,
        # return the API key from the config
        return config['API']['api_key']

def h_duplicate(host, api_key):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    url = 'https://www.babbar.tech/api/host/duplicate'
    data = {
        'host': host,
    }
    response = requests.post(url, headers=headers, params=params, json=data)
    response_data = response.json()
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        time.sleep(60)
        # If the rate limit is reached, sleep for 60 seconds
    csv_data = []
    for item in response_data:
        rank = item["rank"]
        pairs_example = item.get("pairs_example", [])
        # Extract the rank and pairs_example data from the response
        for pair in pairs_example:
            if isinstance(pair, dict):
                source = pair.get("source")
                target = pair.get("target")
                if source is not None and target is not None:
                    csv_data.append([rank, item["percent_from"], item["percent_to"], source, target])
            # Extract the source and target information and append it to the csv_data list
    return csv_data

def main():
    api_key = get_api_key()
    # Retrieve the API key (not shown in the code)
    hosts_file = sys.argv[1] if len(sys.argv) > 1 else 'default_hosts.txt'
    # Get the hosts file from command line arguments or use the default
    if hosts_file == 'default_hosts.txt':
        with open('default_hosts.txt', 'w') as fichier:
            fichier.write('www.babbar.tech')
            # Write the default host to the file if it doesn't exist
    with open(hosts_file, 'r') as f:
        hosts = [line.strip() for line in f]
        # Read the hosts from the file
        for host in hosts:
            with open(f'{host}_internal_duplic.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                if csvfile.tell() == 0:
                    writer.writerow(["rank", "percent_from", "percent_to", "source", "target"])
                    # Write the header row if the file is empty
            response_data = h_duplicate(host, api_key)
            with open(f'{host}_internal_duplic.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(response_data)
                # Write the response data to the CSV file

if __name__ == "__main__":
    main()