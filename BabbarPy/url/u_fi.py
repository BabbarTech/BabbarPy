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
import pandas as pd
import configparser
import os
import sys
import time

def u_fi(source_url, target_url, api_key):
    # Define the URL for the API endpoint
    url = "https://www.babbar.tech/api/url/fi"
    # Set the request headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Set the request parameters with the API key
    params = {'api_token': api_key}
    # Prepare the data payload for the POST request
    data = {
        "source": source_url,
        "target": target_url,
    }
    # Send a POST request to the API endpoint
    response = requests.post(url, headers=headers, params=params, json=data)
    # Extract the remaining rate limit from the response headers
    remain = int(response.headers.get('X-RateLimit-Remaining'))
    # If the rate limit has been exhausted (remaining count is 0), wait for 60 seconds
    if remain == 0:
        time.sleep(60)
    # If the API response is successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response into a DataFrame
        result = response.json()
        df = pd.DataFrame([result])
        # Select specific columns from the DataFrame
        df = df[['source', 'target', 'fi', 'confidence']]
        # Return the resulting DataFrame
        return df
    else:
        # If the API request fails, print an error message with the status code
        print(f"Erreur lors de la requête à l'API : {response.status_code}")

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
    # Retrieve the API key
    api_key = get_api_key()
    # Check if a source file is provided as a command-line argument,
    # otherwise use the default file 'default_2_urls.csv'
    source_file = sys.argv[1] if len(sys.argv) > 1 else 'default_2_urls.csv'
    # If the source file is the default file, create a DataFrame with sample URLs and save it
    if source_file == 'default_2_urls.csv':
        df = pd.DataFrame({'source': ["https://babbar.academy/blog/"],
                           'target': ['https://www.babbar.tech/']})
        df.to_csv(source_file, index=False)
    # Read the source file into a DataFrame
    df = pd.read_csv(source_file)
    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Extract the source and target URLs from the current row
        source = row['source']
        target = row['target']
        # Perform URL translation using the API
        dataf = u_fi(source, target, api_key)
        # Append the results to the 'fi_results.csv' file
        with open("fi_results.csv", 'a', newline='') as f:
            dataf.to_csv(f, header=f.tell() == 0, index=False)
    
if __name__ == "__main__":
    main()