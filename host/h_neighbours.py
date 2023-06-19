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
import configparser
import csv
import requests
import os
import time
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

def h_neighbours(host, api_key):
    # Headers for the API request
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    # Parameters for the API request
    params = {
        'api_token': api_key
    }
    # API endpoint URL
    url = 'https://www.babbar.tech/api/host/neighbours'
    # JSON payload for the API request
    data = {
        'host': host,
    }
    # Send a POST request to the API
    response = requests.post(url, headers=headers, params=params, json=data)
    # Get the remaining rate limit and wait if necessary
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        time.sleep(60)
    # Parse the JSON response
    response_data = response.json()
    return response_data

def main():
    # Get API key
    api_key = get_api_key()
    # Get hosts file from CLI or use default
    hosts_file = sys.argv[1] if len(sys.argv) > 1 else 'default_hosts.txt'
    # Use default hosts file if not provided
    if hosts_file == 'default_hosts.txt':
        with open('default_hosts.txt', 'w') as fichier:
            fichier.write('www.babbar.tech')
    # Read hosts from the file
    with open(hosts_file, 'r') as f:
        hosts = [line.strip() for line in f]
        # Process each host
        for host in hosts:
            # Fetch neighbors data for the current host
            data = h_neighbours(host, api_key)
            # Write links data to a CSV file
            links_data = data["links"]
            links_filename = f"{host}_links.csv"
            with open(links_filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["source", "target", "value"])
                for link in links_data:
                    writer.writerow([link["source"], link["target"], link["value"]])
            # Write nodes data to a CSV file
            nodes_data = data["nodes"]
            nodes_filename = f"{host}_nodes.csv"
            with open(nodes_filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["id", "group", "domain"])
                for node in nodes_data:
                    writer.writerow([node["id"], node["group"], node["domain"]])

if __name__ == "__main__":
    main()