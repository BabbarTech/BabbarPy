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

def semantic_suggests(query, api_key, lang="fr"):
    # Set the headers for the API request
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    # Set the parameters for the API request
    params = {
        'api_token': api_key
    }
    # Define the API URL
    url_api = 'https://www.babbar.tech/api/semantic-explorer/suggests'
    # Prepare the data for the API request
    data = {
        'q': query,
        'lang': lang
    }
    # Send a POST request to the API endpoint
    response = requests.post(url_api, headers=headers, params=params, json=data)
    # Check the remaining rate limit and wait if necessary
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        time.sleep(60)
    # Get the response data in JSON format
    response_data = response.json()
    # Return the response data
    return response_data

def main():
    # Get the API key
    api_key = get_api_key()
    # Get the keywords file from command-line arguments or use the default file
    keywords_file = sys.argv[1] if len(sys.argv) > 1 else 'default_keywords.txt'
    # Create the default keywords file if it doesn't exist
    if keywords_file == 'default_keywords.txt':
        with open('default_keywords.txt', 'w') as fichier:
            fichier.write('choucroute')
    # Read the keywords from the file
    with open(keywords_file, 'r') as f:
        keywords = [line.strip() for line in f]
    # Create a new CSV file for storing the results
    with open('semantic_explorer_suggests.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['query', 'intentions', 'questions'])
    # Iterate over the keywords and make API requests for each query
    for query in keywords:
        semantic_suggests_tocsv(query, api_key, 'fr')

def semantic_suggests_tocsv(query, api_key, lang):
    # Call the semantic_suggests function to retrieve the suggestions for the query
    data = semantic_suggests(query, api_key, lang)
    # Extract the intentions and items from the response data
    intentions = data['intentions']
    items = data['items']
    # Open the CSV file in append mode to add the suggestions
    with open('semantic_explorer_suggests.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Iterate over the items and write each suggestion to a new row in the CSV file
        for item in items:
            title = item['title']
            writer.writerow([query, intentions, title])

if __name__ == "__main__":
    main()