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
import datetime

initial_date = datetime.date.today()-datetime.timedelta(weeks=2)

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

def serp_keywords(keyword, api_key, lang="fr", country="FR", date=initial_date):
    # Set initial values for offset, number of results, and keyword difficulty range
    offset = 0
    n = 100
    min_ = 1
    max_ = 3
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    url = 'https://www.babbar.tech/api/keyword'
    # Prepare the data to be sent in the POST request
    data = {
        'keyword': keyword,
        "lang": lang,
        "country": country,
        "date": date.strftime("%Y-%m-%d"),
        "feature": "ORGANIC",
        "offset": offset,
        "n": n,
        "min": min_,
        "max": max_
    }
    # Send the POST request to retrieve SERP data for the keyword
    response = requests.post(url, headers=headers, params=params, json=data)
    # Check the remaining rate limit and sleep if necessary
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        time.sleep(60)
    # Parse the response data as JSON
    response_data = response.json()
    # Return the response data
    return response_data

def main():
    # Get the API key
    api_key = get_api_key()
    # Define the fieldnames for the CSV file
    fieldnames = ['keywords', 'rank', 'position', 'url', 'date', 'title', 'breadcrumb', 'snippet']
    # Get the keywords file from command line arguments or use the default file
    keywords_file = sys.argv[1] if len(sys.argv) > 1 else 'default_keywords.txt'
    # If the keywords file is the default file, create it with a default keyword
    if keywords_file == 'default_keywords.txt':
        with open('default_keywords.txt', 'w') as fichier:
            fichier.write('babbar')
    # Read the keywords from the file
    with open(keywords_file, 'r') as f:
        keywords = [line.strip() for line in f]
    # Create the CSV file and write the header
    with open('resultats.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    # Iterate over the keywords
    for keyword in keywords:
        # Retrieve SERP data for the keyword
        data = serp_keywords(keyword, api_key)
        # Append the data to the CSV file
        with open('resultats.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for item in data['data']['results']:
                feature = item['feature']
                organic = feature['organic']
                snippet = organic['snippet'].replace('\n', ' ')
                writer.writerow({
                    'keywords': keyword,
                    'rank': item['rank'],
                    'position': organic['position'],
                    'url': organic['url'],
                    'date': data['data']['request']['date'],
                    'title': organic['title'],
                    'breadcrumb': organic['breadcrumb'],
                    'snippet': snippet
                })
    
if __name__ == "__main__":
    main()