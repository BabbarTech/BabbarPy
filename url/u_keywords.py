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

def u_keywords(urls, api_key, start_date, end_date, min =1, max=100, lang ="fr", country="FR"):
    # Convert start_date and end_date strings to datetime objects
    start_datetime = datetime.date(int(start_date.split("-")[0]), int(start_date.split("-")[1]), int(start_date.split("-")[2]))
    end_datetime = datetime.date(int(end_date.split("-")[0]), int(end_date.split("-")[1]), int(end_date.split("-")[2]))
    # Calculate the duration of the date range
    duration = end_datetime - start_datetime
    # Initialize variables
    current_datetime = start_datetime
    periods = duration.days + 1
    api_url = "https://www.babbar.tech/api/url/keywords"
    data_to_export = []
    # Iterate over each day in the date range
    for i in range(periods):
        print("Day " + str(i + 1))
        # Iterate over each URL
        for url in urls:
            # Prepare payload for API request
            payload = {
                "url": url,
                "lang": lang,
                "country": country,
                "date": start_date,
                "offset": 0,
                "n": 500,
                "min": min,
                "max": max,
                "api_token": api_key
            }
            # Send API request to retrieve keyword data
            response = requests.post(api_url, json=payload)
            data = response.json()
            entries = data.get('entries', [])
            # Process each entry and add it to the data_to_export list
            for entry in entries:
                data_to_export.append({
                    'url': entry['url'],
                    'keywords': entry['keywords'],
                    'rank': entry['rank'],
                    'subRank': entry['subRank'],
                    'feature': entry['feature'],
                    'date': current_datetime
                })
        # Increment the current_datetime to the next day
        current_datetime = current_datetime + datetime.timedelta(days=1)
    return data_to_export

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
    # Set the start date to two weeks ago
    date_start = datetime.date.today() - datetime.timedelta(weeks=2)
    date_formatted = date_start.strftime("%Y-%m-%d")
    # Get the API key
    api_key = get_api_key()
    # Get the source file from command line arguments or use default file
    source_file = sys.argv[1] if len(sys.argv) > 1 else 'default_1_url.txt'
    # Define fieldnames for the CSV file
    fieldnames = ['url', 'keywords', 'rank', 'subRank', 'feature', 'date']
    # Create or overwrite the output CSV file with fieldnames as header
    with open('url_keywords_out.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
    # If using the default source file, write a default URL to it
    if source_file == 'default_1_url.txt':
        with open('default_1_url.txt', 'w') as fichier:
            fichier.write('https://www.babbar.tech')
    # Open the source file and read the URLs
    with open(source_file, 'r') as file:
        urls = file.read().splitlines()
        # Call the u_keywords function to retrieve keyword data for the URLs within the specified date range
        data_to_export = u_keywords(urls, api_key, date_formatted, date_formatted)
        # Open the output CSV file in append mode and write the retrieved keyword data
        with open('url_keywords_out.csv', 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writerows(data_to_export)

if __name__ == "__main__":
    main()