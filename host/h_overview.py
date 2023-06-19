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
import csv
import json
import requests
import sys
import configparser
import os
import time

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

def h_overview(host, api_key):
    # API endpoint URL
    endpoint = 'https://www.babbar.tech/api/host/overview/main'
    # Headers for the API request
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Parameters for the API request
    params = {'api_token': api_key}
    # JSON payload for the API request
    payload = {"host": host}
    # Send a POST request to the API
    response = requests.post(endpoint, json=payload, headers=headers, params=params)
    # Get the remaining rate limit and wait if necessary
    remain = int(response.headers.get('X-RateLimit-Remaining'))
    if remain == 0:
        time.sleep(60)
    # Check the response status code and return the data if successful
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f'Data collection error: {response.status_code}')

def write_to_csv(data, dict_writer, host):
    # Write the data to the CSV file using the provided DictWriter
    dict_writer.writerow({
        'host': host,
        'hostValue': data['hostValue'],
        'hostTrust': data['hostTrust'],
        'semanticValue': data['semanticValue'],
        'babbarAuthorityScore': data['babbarAuthorityScore'],
        'knownUrls': data['knownUrls'],
        'backlinks_linkCount': data['backlinks']['linkCount'],
        'backlinks_hostCount': data['backlinks']['hostCount'],
        'backlinks_domainCount': data['backlinks']['domainCount'],
        'backlinks_ipCount': data['backlinks']['ipCount'],
        'backlinks_asCount': data['backlinks']['asCount']
    })

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
    # Keys for the CSV file
    keys = ['host', 'hostValue', 'hostTrust', 'semanticValue', 'babbarAuthorityScore',
            'knownUrls', 'backlinks_linkCount', 'backlinks_hostCount', 'backlinks_domainCount',
            'backlinks_ipCount', 'backlinks_asCount']
    # Create a new CSV file and write the header row
    with open('h_output.csv', 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        # Process each host
        for host in hosts:
            # Fetch overview data for the current host
            data = h_overview(host, api_key)
            # Write the data to the CSV file
            write_to_csv(data, dict_writer, host)

if __name__ == "__main__":
    main()