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

def d_overview(domain, api_key):
    # Set the API endpoint
    endpoint = 'https://www.babbar.tech/api/domain/overview/main'
    # Set the request headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Set the request parameters, including the API key
    params = {'api_token': api_key}
    # Set the request payload, including the domain
    payload = {"domain": domain}
    # Send a POST request to the API endpoint with the headers, parameters, and JSON payload
    response = requests.post(endpoint, json=payload, headers=headers, params=params)
    # Check the remaining rate limit for the API
    remain = int(response.headers.get('X-RateLimit-Remaining'))
    # If the rate limit is exhausted, wait for 60 seconds
    if remain == 0:
        time.sleep(60)
    # If the response status code is 200 (successful), return the response data as a JSON object
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        # If there was an error in data collection, print the response status code
        print(f'Data collection error: {response.status_code}')

def write_to_csv(data, dict_writer, domain):
    # Write the relevant data from the 'data' dictionary to the CSV file using the 'dict_writer'
    dict_writer.writerow({
        'domain': domain,
        'domainValue': data['domainValue'],
        'domainTrust': data['domainTrust'],
        'semanticValue': data['semanticValue'],
        'babbarAuthorityScore': data['babbarAuthorityScore'],
        'knownUrls': data['knownUrls'],
        'backlinks_linkCount': data['backlinks']['linkCount'],
        'backlinks_hostCount': data['backlinks']['hostCount'],
        'backlinks_domainCount': data['backlinks']['domainCount'],
        'backlinks_ipCount': data['backlinks']['ipCount'],
        'backlinks_asCount': data['backlinks']['asCount']
    })

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
    api_key = get_api_key()  # Get the API key
    # Get the domains file from the command-line arguments or use the default file 'default_domains.txt'
    domains_file = sys.argv[1] if len(sys.argv) > 1 else 'default_domains.txt'
    if domains_file == 'default_domains.txt':
        # If using the default domains file, create the file and write 'babbar.tech' to it
        with open('default_domains.txt', 'w') as fichier:
            fichier.write('babbar.tech')
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f]  # Read the domains from the file
    keys = ['domain', 'domainValue', 'domainTrust', 'semanticValue', 'babbarAuthorityScore',
            'knownUrls', 'backlinks_linkCount', 'backlinks_hostCount', 'backlinks_domainCount',
            'backlinks_ipCount', 'backlinks_asCount']
    with open('d_output.csv', 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, keys)  # Create a CSV writer object
        dict_writer.writeheader()  # Write the header row in the CSV file
        for domain in domains:
            data = d_overview(domain, api_key)  # Get the overview data for the domain
            write_to_csv(data, dict_writer, domain)  # Write the data to the CSV file


if __name__ == "__main__":
    main()