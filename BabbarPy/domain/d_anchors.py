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

def d_anchors(domain, api_key):
    # Set the headers for the API request
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    # Set the parameters for the API request
    params = {
        'api_token': api_key
    }
    # Set the URL for the API request
    url = 'https://www.babbar.tech/api/domain/anchors'
    # Set the data for the API request
    data = {
        'domain': domain,
    }
    # Create a list to store all the retrieved data
    all_data = []
    # Send the API request
    response = requests.post(url, headers=headers, params=params, json=data)
    # Get the JSON response data
    response_data = response.json()
    # Check if there are backlinks in the response
    if 'backlinks' in response_data and len(response_data['backlinks']) > 0:
        # Store the backlinks data in the list
        all_data = response_data['backlinks']
        # Check the remaining rate limit
        remain = int(response.headers.get('X-RateLimit-Remaining', 1))
        if remain == 0:
            # If the rate limit is reached, wait for 60 seconds
            print(f"Holding at {data['offset']}")
            time.sleep(60)
    # Return the retrieved data
    return all_data

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

def main():
    # Get the API key
    api_key = get_api_key()
    # Get the domains file from command line arguments or use the default file
    domains_file = sys.argv[1] if len(sys.argv) > 1 else 'default_domains.txt'
    # If the domains file is the default file, create it and write a default domain
    if domains_file == 'default_domains.txt':
        with open('default_domains.txt', 'w') as fichier:
            fichier.write('babbar.tech')
    # Read the domains from the file
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f]
        # Process each domain
        for domain in domains:
            # Create a CSV file for the domain's anchor data
            with open(f'{domain}_anch.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Anchor', 'percent', 'links', 'domains'])
            # Retrieve all the anchor data for the domain
            all_data = d_anchors(domain, api_key)
            # Write the anchor data to the CSV file
            with open(f'{domain}_anch.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                for row in all_data:
                    writer.writerow([row.get('text', ''), row.get('percent', ''), row.get('linkCount', ''), row.get('domainCount', '')])

if __name__ == "__main__":
    main()
