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
import pandas as pd
import requests
import json
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

def h_backlinks_url(host, api_token, sort="desc", type="semanticValue"):
    api_url = "https://www.babbar.tech/api/host/backlinks/url"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "host": host,
        "limit": 30000,
        "sort": sort,
        "type": type
    }
    params = {
        "api_token": api_token
    }
    response = requests.post(api_url, headers=headers, params=params, json=payload)
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        time.sleep(60)
        # If the rate limit is reached, sleep for 60 seconds
    try:
        data = response.json()
        if "links" in data:
            return data["links"]
            # Return the links data if available
        else:
            return []
            # Return an empty list if no links are available
    except json.decoder.JSONDecodeError:
        print("Erreur : Réponse JSON invalide")
        return []
        # Handle JSON decode error and return an empty list

def remove_duplicates_from_csv(file_name):
    df = pd.read_csv(file_name)
    df = df.drop_duplicates()
    df.to_csv(file_name, index=False)
    # Read the CSV file into a DataFrame, remove duplicates, and overwrite the file

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
            data = h_backlinks_url(host, api_key)
            csv_file = f'{host}_bl.csv'
            if not os.path.exists(csv_file):
                with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['source', 'target', 'linkText', 'linkType', 'linkRels', 'language', 'pageValue', 'semanticValue', 'babbarAuthorityScore', 'pageTrust'])
                    # Write the header row to the CSV file if it doesn't exist
            with open(csv_file, 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                for row in data:
                    writer.writerow([row.get('source', ''), row.get('target', ''), row.get('linkText', ''), row.get('linkType', ''), row.get('linkRels', []), row.get('language', ''), row.get('pageValue', ''), row.get('semanticValue', ''), row.get('babbarAuthorityScore', ''), row.get('pageTrust', '')])
                    # Write each row of data to the CSV file
            remove_duplicates_from_csv(csv_file)
            # Remove duplicates from the CSV file

if __name__ == "__main__":
    main()