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

def d_lang(domain, api_key):
    # Set the request headers
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    # Set the request parameters, including the API key
    params = {
        'api_token': api_key
    }
    # Set the URL for the API endpoint
    url = 'https://www.babbar.tech/api/domain/lang'
    # Set the request data, including the domain
    data = {
        'domain': domain,
    }
    # Send a POST request to the API endpoint with the headers, parameters, and JSON data
    response = requests.post(url, headers=headers, params=params, json=data)
    # Parse the response JSON data
    response_data = response.json()
    # Check the remaining rate limit for the API
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    # If the rate limit is exhausted, print a message and wait for 60 seconds
    if remain == 0:
        print(f"holding at {data['offset']}")
        time.sleep(60)
    # Return the response data
    return response_data

def main():
    # Retrieve the API key using the get_api_key function
    api_key = get_api_key()
    # Determine the domains_file based on the command-line arguments. If no argument is provided, it defaults to 'default_domains.txt'.
    domains_file = sys.argv[1] if len(sys.argv) > 1 else 'default_domains.txt'
    # If the domains_file is set to 'default_domains.txt', create and write the default domain 'babbar.tech' to the file.
    if domains_file == 'default_domains.txt':
        with open('default_domains.txt', 'w') as fichier:
            fichier.write('babbar.tech')
    # Open the domains_file and read its content, storing each line as a domain in the domains list.
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f]
        # Iterate over each domain in the domains list
        for domain in domains:
            # Open the 'domain_lang.csv' file for writing (overwrite any existing content)
            with open('domain_lang.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                # Write the header row to the CSV file
                writer.writerow(['domain', 'language', 'percent'])
            # Retrieve the language data for the current domain using the d_lang function and the api_key
            response_data = d_lang(domain, api_key)
            # Open the 'domain_lang.csv' file for appending
            with open('domain_lang.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                # Iterate over each data item in the response_data list
                for data in response_data:
                    # Write the domain, language, and percent as a new row in the CSV file
                    writer.writerow([domain, data['language'], data['percent']])

if __name__ == "__main__":
    main()