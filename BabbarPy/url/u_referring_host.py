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

def u_referring_host(url_b, api_key):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    url = 'https://www.babbar.tech/api/url/backlinks/host'
    data = {
        'url': url_b,
        'n': 499,
        'offset': 0
    }
    all_data = [] 
    # List to store all backlink data
    last_data = None  
    # Variable to track the previous batch of backlinks
    # Continue making requests until no more new backlinks are received
    while True:
        response = requests.post(url, headers=headers, params=params, json=data)
        response_data = response.json()
        numBacklinksUsed = response_data.get('numBacklinksUsed', 0)  
        # Number of backlinks used
        numBacklinksTotal = response_data.get('numBacklinksTotal', 0)  
        # Total number of backlinks
        part_data = response_data.get('backlinks', [])  
        # Partial data containing backlinks
        # Exit the loop when no more new backlinks are received
        if part_data == last_data:
            break
        last_data = part_data
        remain = int(response.headers.get('X-RateLimit-Remaining', 1))
        if remain == 0:
            print(f"holding at {data['offset']}")
            time.sleep(60)
        data['offset'] += len(part_data)  
        # Update the offset for the next batch of backlinks
        all_data.extend(part_data)  
        # Add the current batch of backlinks to the overall list
    return {"all_data": all_data, "numBacklinksUsed": numBacklinksUsed, "numBacklinksTotal": numBacklinksTotal}

def main():
    api_key = get_api_key()
    urls_file = sys.argv[1] if len(sys.argv) > 1 else 'default_urls.txt'
    if urls_file == 'default_urls.txt':
        with open('default_urls.txt', 'w') as fichier:
            fichier.write('https://www.babbar.tech\nhttps://blog.babbar.tech')
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f]
        for url in urls:
            url_c = url.replace("://", "_")
            url_c = url_c.replace("/", "_")
            url_c = url_c.replace(".", "_")
            all_data = u_referring_host(url, api_key)
            # Write backlink data to a CSV file
            with open(f'{url_c}_anchors.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['host', 'anchor text'])
                for row in all_data["all_data"]:
                    anchors = ", ".join([anchor for anchor in row.get('anchors', [])])
                    writer.writerow([row.get('host', ''), anchors])
            # Open file in append mode and only write header if file does not exist.
            file_exists = os.path.isfile('url_list_ref_hosts_overview.csv')
            with open('url_list_ref_hosts_overview.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(['url', 'number of backlinks used', 'Total number of backlinks'])
                writer.writerow([url_c, all_data['numBacklinksUsed'], all_data['numBacklinksTotal']])

if __name__ == "__main__":
    main()