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
import requests
import csv
import time
import configparser
import os
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

def d_similar(api_key, domain):
    # Set JSON payload
    json_payload = {
        "domain": domain,
        "n": 100
    }
    # Set headers
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    # Set parameters
    params = {'api_token': api_key}
    # Set URL
    url = "https://www.babbar.tech/api/domain/similar"
    # Send POST request to fetch similar domains
    response = requests.post(url, headers=headers, params=params, json=json_payload)
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    # Handle rate limiting
    if remain == 0:
        print(f"holding at {domain}")
        time.sleep(60)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse response data as JSON
        data = response.json()
        return data
    else:
        print(f'Request failed with status code {response.status_code}')

def main():
    # Get the API key
    api_key = get_api_key()
    # Get the domains file from the command line arguments or use a default file
    domains_file = sys.argv[1] if len(sys.argv) > 1 else 'default_domains.txt'
    # Write a default domain to the file if the default file is used
    if domains_file == 'default_domains.txt':
        with open('default_domains.txt', 'w') as fichier:
            fichier.write('babbar.tech')
    # Read the domains from the file and process each domain
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f]
        with open('domain_similar.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, ["domain", "similar", "lang", "score"])
            writer.writeheader()
            for domain in domains:
                # Get similar domains data
                data = d_similar(api_key, domain)
                for row in data:
                    row['domain'] = domain
                    writer.writerow(row)

if __name__ == "__main__":
    main()