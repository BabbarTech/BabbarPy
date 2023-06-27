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

def h_fetches(host, lang, API_KEY, data=[""]):
    a = 0
    data_list = []
    url = "https://www.babbar.tech/api/host/fetches/list?api_token=" + API_KEY
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    while True:
        data = {
            "host": host,
            "status": -1,
            "lang": lang,
            "offset": a,
            "n": 499
        }
        resp = requests.post(url, headers=headers, json=data)
        # Send a POST request to the fetches list API endpoint with the host, lang, and API key
        if resp.status_code != 200:
            print("STATUS CODE INVALID")
            print(resp.status_code)
            break
            # If the response status code is not 200, print an error message and break out of the loop
        else:
            try:
                aList = resp.json()
                if isinstance(aList, list):
                    if not aList:
                        print("No more data.")
                        break
                        # If the returned list is empty, print a message and break out of the loop
                    remain = int(resp.headers.get('X-RateLimit-Remaining'))
                    if remain == 0:
                        time.sleep(60)
                        # If the rate limit is reached, sleep for 60 seconds
                    for entry in aList:
                        updated_entry = {
                            'host': host,
                            'url': entry['url'],
                            'lang': entry['lang'],
                            'http': entry['http']
                        }
                        data_list.append(updated_entry)
                        # Extract the required information from the response and add it to the data list
                    a += 1
                    # Increment the offset for the next request
                else:
                    print("Invalid JSON response:", aList)
                    break
                    # If the response is not a valid JSON list, print an error message and break out of the loop
            except ValueError:
                print("Invalid JSON response")
                break
                # If there's an error parsing the JSON response, print an error message and break out of the loop
    return data_list

def h_fetches_to_csv(hosts_file, lang, API):
    data_list = []
    with open(hosts_file, 'r') as f:
        hosts = [line.strip() for line in f]
        # Read the hosts from the file
        for host in hosts:
            data_list.extend(h_fetches(host, lang, API))
            # Fetch the data for each host and extend the data list
    df = pd.DataFrame(data_list, columns=['host', 'url', 'lang', 'http'])
    # Create a DataFrame from the data list
    df.to_csv('hosts_data.csv', index=False)
    # Write the DataFrame to a CSV file without including the index

def main():
    api_key = get_api_key()
    # Retrieve the API key (not shown in the code)
    hosts_file = sys.argv[1] if len(sys.argv) > 1 else 'default_hosts.txt'
    # Get the hosts file from command line arguments or use the default
    if hosts_file == 'default_hosts.txt':
        with open('default_hosts.txt', 'w') as fichier:
            fichier.write('www.babbar.tech')
            # Write the default host to the file if it doesn't exist
    h_fetches_to_csv(hosts_file, 'all', api_key)
    # Fetch the data for hosts in the hosts file and write it to a CSV file

if __name__ == "__main__":
    main()
