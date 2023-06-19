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
    
def u_referring_domain(url, api_key):
    # Set the request headers
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    # Set the request parameters including the API key
    params = {
        'api_token': api_key
    }
    # Set the API URL
    url_api = 'https://www.babbar.tech/api/url/backlinks/domain'
    # Set the initial request data
    data = {
        'url': url,
        'n': 500,
        'offset': 0
    }
    # Initialize a list to store all the data
    all_data = []
    # Make requests until all backlinks are retrieved
    while True:
        # Send the POST request to the API
        response = requests.post(url_api, headers=headers, params=params, json=data)
        # Parse the response JSON
        response_data = response.json()
        # Check if backlinks are present in the response
        if 'backlinks' in response_data and len(response_data['backlinks']) > 0:
            # Store the backlinks data
            all_data = response_data['backlinks']
            # Get the number of backlinks used and total backlinks
            numBacklinksUsed = response_data.get('numBacklinksUsed', 0)
            numBacklinksTotal = response_data.get('numBacklinksTotal', 0)
            # Check the rate limit and wait if necessary
            remain = int(response.headers.get('X-RateLimit-Remaining', 1))
            if remain == 0:
                print(f"holding at {data['offset']}")
                time.sleep(60)
            # Increment the offset to retrieve the next set of backlinks
            data['offset'] += 1
            # Return the collected data and backlink counts
            return {"all_data": all_data, "numBacklinksUsed": numBacklinksUsed, "numBacklinksTotal": numBacklinksTotal}
        # Break the loop if no backlinks are present
        break

def main():
    api_key = get_api_key()
    urls_file = sys.argv[1] if len(sys.argv) > 1 else 'default_urls.txt'
    # Check if the default URLs file is used and create it if necessary
    if urls_file == 'default_urls.txt':
        with open('default_urls.txt', 'w') as fichier:
            fichier.write('https://www.babbar.tech')
    # Read the URLs from the file
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f]
        # Create the CSV file for storing the overview data
        with open('url_list_ref_domains_overview.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['url', 'number of backlinks used', 'Total number of backlinks'])
        # Process each URL
        for url in urls:
            # Format the URL to create a valid filename
            url_n = url.replace("://", "_")
            url_n = url_n.replace(".", "_")
            url_n = url_n.replace("/", "_")
            # Retrieve the referring domain backlinks data
            dict_data = u_referring_domain(url, api_key)
            all_data = dict_data['all_data']
            numBacklinksUsed = dict_data['numBacklinksUsed']
            numBacklinksTotal = dict_data['numBacklinksTotal']
            # Create a separate CSV file for storing the anchor text data
            with open(f'{url_n}_u_anchors.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['domain', 'anchor text'])
            # Write the anchor text data to the CSV file
            with open(f'{url_n}_u_anchors.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                for row in all_data:
                    anchors = ", ".join([anchor for anchor in row.get('anchors', [])])
                    writer.writerow([row.get('domain', ''), anchors])
            # Write the overview data to the main CSV file
            with open('url_list_ref_domains_overview.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([url, numBacklinksUsed, numBacklinksTotal])

if __name__ == "__main__":
    main()