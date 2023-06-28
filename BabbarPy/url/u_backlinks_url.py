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
import json
import time
import pandas as pd

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

def u_backlinks_url(url, api_token, sort="desc", type="semanticValue"):
    # Specify the API endpoint URL
    api_url = "https://www.babbar.tech/api/url/backlinks/url"
    # Set the request headers
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    # Set the payload for the API request
    payload = {
        "url": url,
        "limit": 30000,
        "sort": sort,
        "type": type
    }
    # Set the API token in the request parameters
    params = {
        "api_token": api_token
    }
    # Send a POST request to the API endpoint
    response = requests.post(api_url, headers=headers, params=params, json=payload)
    # Check the rate limit remaining
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        # If rate limit reached, wait for 60 seconds
        time.sleep(60)
    try:
        # Parse the response JSON
        data = response.json()
        # Check if the "links" key exists in the response data
        if "links" in data:
            # Return the list of backlinks
            return data["links"]
        else:
            # If no backlinks found, return an empty list
            return []
    except json.decoder.JSONDecodeError:
        # Handle JSON decoding error and return an empty list
        print("Erreur : Réponse JSON invalide")
        return []

def remove_duplicates_from_csv(file_name):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_name)
    # Remove duplicate rows
    df = df.drop_duplicates()
    # Save the DataFrame back to the CSV file without index
    df.to_csv(file_name, index=False)

def main():
        # Get the API key
    api_key = get_api_key()
    # Get the URLs file from command-line arguments or use the default file
    urls_file = sys.argv[1] if len(sys.argv) > 1 else 'default_urls.txt'
    # If using the default URLs file, create it and populate with default URLs
    if urls_file == 'default_urls.txt':
        with open('default_urls.txt', 'w') as fichier:
            fichier.write('https://blog.babbar.tech/\nhttps://www.babbar.tech/')
    # Read the URLs from the file
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f]
        # Iterate over each URL
        for url in urls:
            # Retrieve backlink data for the URL
            data = u_backlinks_url(url, api_key)
            # Modify the URL to create a corresponding CSV file name
            url_c = url.replace('://','_')
            url_c = url_c.replace('/','_')
            url_c = url_c.replace('.','')
            csv_file = f'{url_c}_bl.csv'
            # If the CSV file doesn't exist, create it and write the header row
            if not os.path.exists(csv_file):
                with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['source', 'target', 'linkText', 'linkType', 'linkRels', 'language', 'pageValue', 'semanticValue', 'babbarAuthorityScore', 'pageTrust'])
            # Append the retrieved data to the CSV file
            with open(csv_file, 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                for row in data:
                    writer.writerow([row.get('source', ''), row.get('target', ''), row.get('linkText', ''), row.get('linkType', ''), row.get('linkRels', []), row.get('language', ''), row.get('pageValue', ''), row.get('semanticValue', ''), row.get('babbarAuthorityScore', ''), row.get('pageTrust', '')])
            # Remove duplicate rows from the CSV file
            remove_duplicates_from_csv(csv_file)

if __name__ == "__main__":
    main()