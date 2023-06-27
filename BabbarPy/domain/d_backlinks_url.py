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

def d_backlinks_url(domain, api_key, sort='desc', type_='semanticValue'):
    # Set the headers and parameters for the API request
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    url = 'https://www.babbar.tech/api/domain/backlinks/url'
    # Set the data payload for the API request
    data = {
        'domain': domain,
        'limit': 30000,
        'sort': sort,
        'type': type_
    }
    all_data = []  # to store all the retrieved data
    # Send the API request
    response = requests.post(url, headers=headers, params=params, json=data)
    response_data = response.json()
    # Check if there are links in the response and retrieve them
    if 'links' in response_data and len(response_data['links']) > 0:
        part_data = response_data['links']
        all_data.extend(part_data)
        # Check the remaining rate limit and wait if necessary
        remain = int(response.headers.get('X-RateLimit-Remaining', 1))
        if remain == 0:
            print(f"Holding at offset: {data['offset']}")
            time.sleep(60)
    return all_data

def main():
    # Get the API key
    api_key = get_api_key()
    # Get the domains file from command line argument or use default
    domains_file = sys.argv[1] if len(sys.argv) > 1 else 'default_domains.txt'
    # If using the default domains file, create it with a default domain
    if domains_file == 'default_domains.txt':
        with open('default_domains.txt', 'w') as fichier:
            fichier.write('babbar.tech')
    # Read the domains from the file
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f]
        # Process each domain
        for domain in domains:
            # Open a CSV file for writing backlink data for the domain
            with open(f'{domain}_bl.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['source', 'target', 'linkText', 'linkType', 'linkRels', 'language', 'pageValue', 'semanticValue', 'babbarAuthorityScore', 'pageTrust'])
            # Retrieve backlink data for the domain
            all_data = d_backlinks_url(domain, api_key)
            # Append the backlink data to the CSV file
            with open(f'{domain}_bl.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                for row in all_data:
                    writer.writerow([row.get('source', ''), row.get('target', ''), row.get('linkText', ''), row.get('linkType', ''), row.get('linkRels', []), row.get('language', ''), row.get('pageValue', ''), row.get('semanticValue', ''), row.get('babbarAuthorityScore', ''), row.get('pageTrust', '')])

if __name__ == "__main__":
    main()