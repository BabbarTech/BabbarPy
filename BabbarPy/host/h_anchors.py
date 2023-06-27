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

def h_anchors(host, api_key):
    # Set headers
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    # Set parameters
    params = {
        'api_token': api_key
    }
    # Set URL
    url = 'https://www.babbar.tech/api/host/anchors'
    # Set data payload
    data = {
        'host': host,
    }
    # Initialize list to store retrieved data
    all_data = []
    # Send POST request to fetch anchors for the host
    response = requests.post(url, headers=headers, params=params, json=data)
    response_data = response.json()
    # Check if there are backlinks in the response
    if 'backlinks' in response_data and len(response_data['backlinks']) > 0:
        # Store the backlinks data
        all_data = response_data['backlinks']
        # Check rate limiting
        remain = int(response.headers.get('X-RateLimit-Remaining', 1))
        if remain == 0:
            print(f"holding at{data['offset']}")
            time.sleep(60)
    return all_data

def main():
    # Get API key
    api_key = get_api_key()
    # Get hosts file from CLI or use default
    hosts_file = sys.argv[1] if len(sys.argv) > 1 else 'default_hosts.txt'
    # Use default hosts file if not provided
    if hosts_file == 'default_hosts.txt':
        with open('default_hosts.txt', 'w') as fichier:
            fichier.write('www.babbar.tech')
    # Read hosts from the file
    with open(hosts_file, 'r') as f:
        hosts = [line.strip() for line in f]
        # Process each host
        for host in hosts:
            # Create a CSV file for storing anchor data
            with open(f'{host}_anch.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Anchor', 'percent', 'links', 'hosts'])
            # Fetch anchor data for the host
            all_data = h_anchors(host, api_key)
            # Append anchor data to the CSV file
            with open(f'{host}_anch.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                for row in all_data:
                    writer.writerow([row.get('text', ''), row.get('percent', ''), row.get('linkCount', ''), row.get('hostCount', '')])

if __name__ == "__main__":
    main()