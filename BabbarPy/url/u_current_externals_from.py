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
import pandas as pd
import sys
import configparser
import os
import datetime
import time

# Définir les paramètres communs
def u_current_externals_from(url, api_key):
    # Set the request headers
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    # Set the request parameters with the API key
    params = {
        'api_token': api_key
    }
    # Define the API endpoint URL
    url_api = 'https://www.babbar.tech/api/url/linksExternal'
    # Prepare the data payload for the POST request
    data = {
        'url': url,
    }
    # Send a POST request to the API endpoint
    response = requests.post(url_api, headers=headers, params=params, json=data)
    # Get the remaining rate limit from the response headers
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    # If the rate limit is exhausted (remaining count is 0), wait for 60 seconds
    if remain == 0:
        print(f"holding at {data['offset']}")
        time.sleep(60)
    # Parse the response data as JSON and retrieve the 'links' data
    response_data = response.json()['links']
    # Return the 'links' data
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
    # Retrieve the API key
    api_key = get_api_key()
    # Check if a source file is provided as a command-line argument, otherwise use the default file 'default_1_url.txt'
    source_file = sys.argv[1] if len(sys.argv) > 1 else 'default_1_url.txt'
    # Define the fieldnames for the CSV file
    fieldnames = ["url", "target", "linkType", "linkRels", "linkText"]
    # Create a new CSV file and write the header row
    with open('url_externals.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
    # If the source file is the default file, create it and write a sample URL
    if source_file == 'default_1_url.txt':
        with open('default_1_url.txt', 'w') as fichier:
            fichier.write('https://www.babbar.tech')
    # Read the URLs from the source file
    with open(source_file, 'r') as file:
        urls = file.read().splitlines()
        # Process each URL
        for url in urls:
            # Modify the URL to create a unique filename
            url_n = url.replace("://", "_")
            url_n = url_n.replace(".", "_")
            url_n = url_n.replace("/", "_")
            # Retrieve external links data for the URL
            links_data = u_current_externals_from(url, api_key)
            # Write the links data to the CSV file
            with open('url_externals.csv', 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                # Write each link as a row in the CSV file
                for link in links_data:
                    row = {
                        "url": url,
                        "target": link["target"],
                        "linkType": link["linkType"],
                        "linkRels": "|||".join(link["linkRels"]) if link["linkRels"] else "",
                        "linkText": link["linkText"]
                    }
                    writer.writerow(row)

if __name__ == "__main__":
    main()