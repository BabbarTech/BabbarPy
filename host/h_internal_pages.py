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
import pandas as pd
import requests
from requests.structures import CaseInsensitiveDict
import time
import configparser
import sys
import os

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

def h_internal_pages(host, API_KEY):
    a = 0
    list01 = [" "]
    pages = pd.DataFrame()
    url = "https://www.babbar.tech/api/host/pages/internal?api_token=" + API_KEY
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    while list01 != []:
        data = '{"host": "' + str(host) + '", "offset": ' + str(a) + ', "n": 500}'
        resp = requests.post(url, headers=headers, data=data)
        # Send a POST request to the API with the necessary headers and data
        if resp.status_code != 200:
            print("STATUS CODE INVALID")
            print(resp.status_code)
            list01 = []
            break
            # Break the loop if the status code is invalid
        else:
            remain = int(resp.headers.get('X-RateLimit-Remaining'))
            if remain == 0:
                time.sleep(60)
                # Sleep for 60 seconds if the rate limit is reached
            list01 = resp.json()
            # Get the JSON response from the API
            pages_fetch = pd.DataFrame(list01, columns=['url', 'inLinksExternal', 'inLinksInternal', 'pageValue', 'pageTrust', 'semanticValue', 'internalElementValue'])
            # Create a DataFrame from the fetched data
            pages = pd.concat([pages, pages_fetch])
            a = a + 1
    return pages
    # Return the collected internal pages

def internal_pages_to_csv(host, API):
    df = h_internal_pages(host, API)
    # Fetch the internal pages for the host
    df.to_csv(f'{host}_internalpages.csv')
    # Save the DataFrame to a CSV file

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
            internal_pages_to_csv(host, api_key)
            # Save the internal pages to a CSV file for each host

if __name__ == "__main__":
    main()