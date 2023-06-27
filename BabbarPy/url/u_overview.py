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
import time
import configparser
import os
import sys
import csv

def u_overview(fetch_url, API):
    # API endpoint URL
    url = "https://www.babbar.tech/api/url/overview/main"
    # Set headers for the HTTP request
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Create data dictionary with the URL to fetch overview for
    data = {"url": fetch_url}
    # Create params dictionary with the API key
    params = {"api_token": API}
    # Send POST request to the API endpoint
    response = requests.post(url, headers=headers, params=params, json=data)
    # Check remaining API rate limit
    remain = int(response.headers.get('X-RateLimit-Remaining'))
    if remain == 0:
        # If limit is 0, wait for 60 seconds before making another request
        time.sleep(60)
    if response.status_code == 200:
        # If the response status code is 200 (success), parse the JSON response
        result_dict = response.json()
        return result_dict
    else:
        # If the response status code is not 200, print an error message
        print("Request failed with status code", response.status_code)

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
    # Get the API key
    api_key = get_api_key()
    # Read the source file from command line arguments or use a default file
    source_file = sys.argv[1] if len(sys.argv) > 1 else 'default_1_url.txt'
    # Create a default source file if using the default filename
    if source_file == 'default_1_url.txt':
        with open('default_1_url.txt', 'w') as fichier:
            fichier.write('https://www.babbar.tech')
    # Create a dictionary to store the overview data
    mydictionary = {
        "url": [],
        "pageValue": [],
        "pageTrust": [],
        "semanticValue": [],
        "babbarAuthorityScore": [],
        "backlinks": [],
        "referringhosts": []
    }
    # Read the URLs from the source file and fetch overview data
    with open(source_file, 'r') as file:
        for url in file:
            # Remove newline character from the URL
            url_foo = url.replace("\n", "")
            # Fetch overview data for the URL using the u_overview function
            temp_dict = u_overview(url_foo, api_key)
            # Add the URL to the dictionary
            mydictionary["url"].append(url_foo)
            if temp_dict is not None:
                # If overview data is available, extract and add relevant values to the dictionary
                if "pageValue" in temp_dict:
                    mydictionary["pageValue"].append(temp_dict["pageValue"])
                else:
                    mydictionary["pageValue"].append(None)
                if "pageTrust" in temp_dict:
                    mydictionary["pageTrust"].append(temp_dict["pageTrust"])
                else:
                    mydictionary["pageTrust"].append(None)
                if "semanticValue" in temp_dict:
                    mydictionary["semanticValue"].append(temp_dict["semanticValue"])
                else:
                    mydictionary["semanticValue"].append(None)
                if "babbarAuthorityScore" in temp_dict:
                    mydictionary["babbarAuthorityScore"].append(temp_dict["babbarAuthorityScore"])
                else:
                    mydictionary["babbarAuthorityScore"].append(None)
                if "backlinks" in temp_dict:
                    if "linkCount" in temp_dict["backlinks"]:
                        mydictionary["backlinks"].append(temp_dict["backlinks"]["linkCount"])
                    else:
                        mydictionary["backlinks"].append(None)
                    if "hostCount" in temp_dict["backlinks"]:
                        mydictionary["referringhosts"].append(temp_dict["backlinks"]["hostCount"])
                    else:
                        mydictionary["referringhosts"].append(None)
                else:
                    mydictionary["backlinks"].append(None)
                    mydictionary["referringhosts"].append(None)
            else:
                # Add None values to all dictionary keys in case temp_dict is None
                mydictionary["pageValue"].append(None)
                mydictionary["pageTrust"].append(None)
                mydictionary["semanticValue"].append(None)
                mydictionary["babbarAuthorityScore"].append(None)
                mydictionary["backlinks"].append(None)
                mydictionary["referringhosts"].append(None)
    # Write the overview data to a CSV file
    with open("output.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        # Write the header row using the dictionary keys as column names
        writer.writerow(mydictionary.keys())
        # Write the data rows by transposing the dictionary values
        writer.writerows(zip(*mydictionary.values()))

if __name__ == "__main__":
    main()