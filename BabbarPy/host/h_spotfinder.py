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
import time
import configparser
import os
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

def h_spotfinder(term, api_key):
    # API endpoint URL
    url = 'https://www.babbar.tech/api/host/spotsfinder'
    # Headers for the API request
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Parameters for the API request
    params = {'api_token': api_key}
    # Data payload for the API request
    data = {'content': term, 'lang': 'fr'}
    # Send a POST request to the API
    response = requests.post(url, headers=headers, params=params, json=data)
    # Check rate limit and wait if necessary
    if 'X-RateLimit-Remaining' in response.headers:
        remain = int(response.headers.get('X-RateLimit-Remaining'))
        if remain == 0:
            time.sleep(60)
    # Check if the response is successful
    if response.status_code != 200:
        print(f'Data collection error: {response.status_code}')
        return []
    else:
        # Parse the response JSON
        results = response.json()
        # Process the results and create rows for CSV
        rows = []
        for result in results:
            row = [term, result['host'], result['score']]
            urls = result['urls']
            for i in range(3):
                if i < len(urls):
                    row.extend([urls[i]['similar'], urls[i]['score']])
                else:
                    row.extend(['', ''])
            rows.append(row)
        return rows

def main():
    # Get API key
    api_key = get_api_key()
    # Get terms file from CLI or use default
    terms_file = sys.argv[1] if len(sys.argv) > 1 else 'default_terms.txt'
    # Use default terms file if not provided
    if terms_file == 'default_terms.txt':
        with open('default_terms.txt', 'w') as fichier:
            fichier.write('babbar et yourtext guru les meilleurs outil seo')
    # Create a new CSV file and write the header row
    with open('spotfinder_results.csv', 'w', newline='') as foo:
        writer = csv.writer(foo, lineterminator='\n')
        writer.writerow(['query', 'host', 'score', 'urls similar 1', 'score 1', 'urls similar 2', 'score 2', 'urls similar 3', 'score 3'])
        # Read terms from the file
        with open(terms_file, 'r') as f:
            terms = [line.strip() for line in f]
            # Process each term
            for term in terms:
                # Fetch spotfinder results for the term
                rows = h_spotfinder(term, api_key)
                # Write rows to the CSV file
                for row in rows:
                    writer.writerow(row)

if __name__ == "__main__":
    main()