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

def u_anchors(url, api_key):
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
    url_api = 'https://www.babbar.tech/api/url/anchors'
    # Prepare the data payload for the POST request
    data = {
        'url': url,
    }
    # Create a list to store all the retrieved data
    all_data = []
    # Send a POST request to the API endpoint
    response = requests.post(url_api, headers=headers, params=params, json=data)
    # Parse the response data as JSON
    response_data = response.json()
    # Check if 'backlinks' key is present in the response data and if it contains any data
    if 'backlinks' in response_data and len(response_data['backlinks']) > 0:
        # Retrieve the 'backlinks' data and store it in the 'all_data' list
        all_data = response_data['backlinks']
        # Get the remaining rate limit from the response headers
        remain = int(response.headers.get('X-RateLimit-Remaining', 1))
        # If the rate limit is exhausted (remaining count is 0), wait for 60 seconds
        if remain == 0:
            print(f"holding at {data['offset']}")
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
    # Retrieve the API key
    api_key = get_api_key()
    # Check if a URLs file is provided as a command-line argument, otherwise use the default file 'default_urls.txt'
    urls_file = sys.argv[1] if len(sys.argv) > 1 else 'default_urls.txt'
    # If the URLs file is the default file, create it and write a sample URL
    if urls_file == 'default_urls.txt':
        with open('default_urls.txt', 'w') as fichier:
            fichier.write('https://www.babbar.tech')
    # Read the URLs from the file into a list
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f]
        # Process each URL
        for url in urls:
            # Create a filename based on the modified URL
            url_n = url.replace("://", "_")
            url_n = url_n.replace(".", "_")
            url_n = url_n.replace("/", "_")
            # Create a new CSV file with headers
            with open(f'{url_n}_anch.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Anchor', 'Percent', 'Links', 'Hosts'])
            # Retrieve backlink data for the URL
            all_data = u_anchors(url, api_key)
            # Append the backlink data to the CSV file
            with open(f'{url_n}_anch.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                for row in all_data:
                    writer.writerow([row.get('text', ''), row.get('percent', ''), row.get('linkCount', ''), row.get('hostCount', '')])

if __name__ == "__main__":
    main()