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

def d_referring_host(domain, api_key):
    # Set headers and parameters
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    # Set API endpoint and data payload
    url = 'https://www.babbar.tech/api/domain/backlinks/host'
    data = {
        'domain': domain,
        'n': 500,
        'offset': 0
    }
    # Initialize variables
    all_data = []
    # Fetch data in batches until all backlinks are retrieved
    while True:
        response = requests.post(url, headers=headers, params=params, json=data)
        response_data = response.json()
        # Check if backlinks exist in the response
        if 'backlinks' in response_data and len(response_data['backlinks']) > 0:
            all_data = response_data['backlinks']
            numBacklinksUsed = response_data.get('numBacklinksUsed', 0)
            numBacklinksTotal = response_data.get('numBacklinksTotal', 0)
            remain = int(response.headers.get('X-RateLimit-Remaining', 1))
            # Handle rate limiting
            if remain == 0:
                print(f"holding at {data['offset']}")
                time.sleep(60)
            data['offset'] += 1
            return {
                "all_data": all_data,
                "numBacklinksUsed": numBacklinksUsed,
                "numBacklinksTotal": numBacklinksTotal
            }
        break

def main():
    # Get the API key
    api_key = get_api_key()
    # Get the domains file from the command line arguments or use a default file
    domains_file = sys.argv[1] if len(sys.argv) > 1 else 'default_domains.txt'
    # Write a default domain to the file if the default file is used
    if domains_file == 'default_domains.txt':
        with open('default_domains.txt', 'w') as fichier:
            fichier.write('babbar.tech')
    # Read the domains from the file and store them in a list
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f]
        # Create the output CSV file for domain list with referring hosts overview
        with open('domain_list_ref_hosts_overview.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['domain', 'number of backlinks used', 'Total number of backlinks'])
        # Process each domain
        for domain in domains:
            # Get referring hosts data
            dict_data = d_referring_host(domain, api_key)
            all_data = dict_data['all_data']
            numBacklinksUsed = dict_data['numBacklinksUsed']
            numBacklinksTotal = dict_data['numBacklinksTotal']
            # Create the output CSV file for domain anchors
            with open(f'{domain}_anchors.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['host', 'anchor text'])
            # Write data to domain anchors CSV file
            with open(f'{domain}_anchors.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                for row in all_data:
                    anchors = ", ".join([anchor for anchor in row.get('anchors', [])])
                    writer.writerow([row.get('host', ''), anchors])
            # Write data to domain list with referring hosts overview CSV file
            with open('domain_list_ref_hosts_overview.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([domain, numBacklinksUsed, numBacklinksTotal])

if __name__ == "__main__":
    main()