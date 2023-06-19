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

def semantic_mindreader(query, api_key, lang="fr"):
    # Set the request headers and parameters
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    # Define the API endpoint URL
    url_api = 'https://www.babbar.tech/api/semantic-explorer/mindreader'
    # Prepare the request payload (query and language)
    data = {
        'q': query,
        'lang': lang
    }
    # Send a POST request to the API
    response = requests.post(url_api, headers=headers, params=params, json=data)
    # Check the rate limit and wait if necessary
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        time.sleep(60)
    # Get the response data in JSON format
    response_data = response.json()
    # Return the response data
    return response_data

def main():
    # Obtain the API key
    api_key = get_api_key()
    # Read the keywords from a file or use default keywords
    keywords_file = sys.argv[1] if len(sys.argv) > 1 else 'default_keywords.txt'
    if keywords_file == 'default_keywords.txt':
        # If the default keywords file is used, create it and write a default keyword
        with open('default_keywords.txt', 'w') as fichier:
            fichier.write('choucroute')
    with open(keywords_file, 'r') as f:
        keywords = [line.strip() for line in f]
    # Create a new CSV file to store the semantic exploration results
    with open('semantic_explorer_mindreader.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['query', 'intentions', 'questions'])
    # Iterate through each keyword and perform semantic exploration
    for query in keywords:
        # Call the semantic_mindreader_tocsv function to retrieve semantic exploration results
        semantic_mindreader_tocsv(query, api_key, 'fr')
        
def semantic_mindreader_tocsv(query, api_key, lang):
    # Perform semantic exploration using the semantic_mindreader function
    data = semantic_mindreader(query, api_key, lang)
    # Extract intentions and items from the response data
    intentions = data['intentions']
    items = data['items']
    # Append the semantic exploration results to the existing CSV file
    with open('semantic_explorer_mindreader.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Iterate through each item and write the query, intentions, and item title to the CSV file
        for item in items:
            title = item['title']
            writer.writerow([query, intentions, title])

if __name__ == "__main__":
    main()