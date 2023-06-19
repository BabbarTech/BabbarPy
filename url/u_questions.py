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

def u_questions(url, api_key):
    # Set the headers and parameters for the API request
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    # Set the URL for the API endpoint
    url_api = 'https://www.babbar.tech/api/url/questions'
    # Set the data payload for the API request
    data = {
        'url': url
    }
    # Send a POST request to the API endpoint with the headers, parameters, and JSON data
    response = requests.post(url_api, headers=headers, params=params, json=data)
    # Get the JSON response data
    response_data = response.json()
    # Check the remaining rate limit and wait if it reaches zero
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        print(f"holding at {data['offset']}")
        time.sleep(60)
    # Return the response data
    return response_data

def main():
    # Get the API key
    api_key = get_api_key()
    # Define the field names for the CSV file
    fields = ["url", "lang", "question", "score"]
    # Get the URLs file from the command line arguments or use the default file
    urls_file = sys.argv[1] if len(sys.argv) > 1 else 'default_urls.txt'
    # Create the default URLs file if it doesn't exist
    if urls_file == 'default_urls.txt':
        with open('default_urls.txt', 'w') as fichier:
            fichier.write('https://blog.babbar.tech/')
    # Read the URLs from the file
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f]
        # Create the CSV file and write the header row
        with open('url_questions_list.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
        # Process each URL
        for url in urls:
            # Retrieve the questions for the URL
            dict_data = u_questions(url, api_key)
            # Append the questions to the CSV file
            with open('url_questions_list.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                for item in dict_data:
                    item["url"] = url
                    writer.writerow(item)

if __name__ == "__main__":
    main()