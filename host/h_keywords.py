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
import datetime
import pandas as pd
import requests
from requests.structures import CaseInsensitiveDict
import time
import configparser
import sys
import os

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

def h_keywords(host, lang, country, start_date, end_date, api_key):
    # Convert start and end dates to datetime objects
    start_datetime = datetime.date(int(start_date.split("-")[0]), int(start_date.split("-")[1]),
                                   int(start_date.split("-")[2]))
    end_datetime = datetime.date(int(end_date.split("-")[0]), int(end_date.split("-")[1]),
                                 int(end_date.split("-")[2]))
    duration = end_datetime - start_datetime
    current_datetime = start_datetime
    a = 0
    list01 = [" "]
    kws = pd.DataFrame()  
    # Initialize an empty DataFrame to store the keywords
    kws_bydate = pd.DataFrame()  
    # Initialize an empty DataFrame to store the keywords by date
    url = "https://www.babbar.tech/api/host/keywords"  
    # API URL
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    periods = duration.days + 1  
    # Calculate the number of days to loop over
    for i in range(periods):
        print("day " + str(i + 1))
        date = str(current_datetime.year) + '-' + str(current_datetime.month) + '-' + str(current_datetime.day)
        while list01 != []:
            data = {
                'host': host,
                'lang': lang,
                'country': country,
                'date': date,
                'offset': a,
                'n': 500,
                'min': 1,
                'max': 100
            }
            resp = requests.post(url, headers=headers, params={'api_token': api_key}, json=data)
            # Send a POST request to the API with the necessary data and headers
            if resp.status_code != 200:
                print("STATUS CODE INVALID")
                print(resp.status_code)
                list01 = []
                break
            else:
                aDict = resp.json()  
                # Get the JSON response from the API
                remain = int(resp.headers.get('X-RateLimit-Remaining'))
                if remain == 0:
                    time.sleep(60)  
                    # Sleep for 60 seconds if the rate limit is reached
                list01 = aDict['entries']  
                # Extract the list of keywords from the response
                kws_fetch = pd.DataFrame(list01,
                                         columns=['feature', 'rank', 'subRank', 'keywords', 'url', 'numberOfWordsInKeyword',
                                                  'bks'])
                kws_bydate = pd.concat([kws_bydate, kws_fetch])  
                # Append the fetched keywords to kws_bydate DataFrame
                kws_bydate['date'] = current_datetime  
                # Add the current date to the DataFrame
                a = a + 1
        current_datetime = current_datetime + datetime.timedelta(days=1)  
        # Move to the next date
        kws = pd.concat([kws, kws_bydate])  
        # Append the keywords of the current date to the main DataFrame
        a = 0
        list01 = [" "]  
        # Reset the list of keywords
    return kws  
    # Return the final DataFrame with all keywords

def babbar_keywords_to_csv(host, lang, country, start_date, end_date, api_key):
    df = h_keywords(host, lang, country, start_date, end_date, api_key)
    df.to_csv(f'{host}_keywords.csv')  
    # Save DataFrame to a CSV file

def main():
    api_key = get_api_key()  
    # Retrieve the API key (not shown in the code)
    hosts_file = sys.argv[1] if len(sys.argv) > 1 else 'default_hosts.txt'  
    # Get the hosts file from command line arguments or use the default
    date_start = datetime.date.today() - datetime.timedelta(weeks=2)  
    # Calculate the start date
    date_formatted = date_start.strftime("%Y-%m-%d")  
    # Format the start date as a string
    if hosts_file == 'default_hosts.txt':
        with open('default_hosts.txt', 'w') as fichier:
            fichier.write('www.babbar.tech')  
            # Write the default host to the file if it doesn't exist
    with open(hosts_file, 'r') as f:
        hosts = [line.strip() for line in f]  
        # Read the hosts from the file
        for host in hosts:
            babbar_keywords_to_csv(host, 'fr', 'FR', date_formatted, date_formatted, api_key)  
            # Fetch and save keywords for each host

if __name__ == "__main__":
    main()