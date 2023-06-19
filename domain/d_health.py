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

def d_health(domain, api_key):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    url = 'https://www.babbar.tech/api/domain/health'
    data = {
        'domain': domain,
    }
    # Send a POST request to the API endpoint
    response = requests.post(url, headers=headers, params=params, json=data)
    # Extract the JSON response
    response_data = response.json()
    # Check the remaining rate limit and wait for 60 seconds if it reaches 0
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        print(f"Holding at {data['offset']}")
        time.sleep(60)
    # Return the response data
    return response_data

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
    api_key = get_api_key()
    domains_file = sys.argv[1] if len(sys.argv) > 1 else 'default_domains.txt'
    # If the domains file is set to the default value, create and write 'babbar.tech' to the file
    if domains_file == 'default_domains.txt':
        with open('default_domains.txt', 'w') as fichier:
            fichier.write('babbar.tech')
    # Read the domains from the file
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f]
        # Iterate over each domain
        for domain in domains:
            with open(f'{domain}_health.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['domain', 'health', 'h2xx', 'h3xx', 'h4xx', 'h5xx', 'Total', 'failed'])
            # Get the health information for the domain
            response_data = d_health(domain, api_key)
            # Write the health information to the CSV file
            with open(f'{domain}_health.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    domain,
                    response_data.get('health', ''),
                    response_data.get('h2xx', ''),
                    response_data.get('h3xx', ''),
                    response_data.get('h4xx', ''),
                    response_data.get('h5xx', ''),
                    response_data.get('hxxx', ''),
                    response_data.get('hfailed', '')
                ])

if __name__ == "__main__":
    main()
