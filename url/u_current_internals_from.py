"""
MIT License

Copyright (c) 2023 BabbarTech & PierreFECalvet

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
import time

# Définir les paramètres communs
def u_current_internals_from(url, api_key):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    url_api = 'https://www.babbar.tech/api/url/linksInternal'
    data = {
        'url': url,
    }
    response = requests.post(url_api, headers=headers, params=params, json=data)
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        print(f"holding at{data['offset']}")
        time.sleep(60)
    response_data = response.json()['links']
    return response_data

def get_api_key():
    config = configparser.ConfigParser()
    if not os.path.exists('config.ini') or not config.read('config.ini') or not 'API' in config or not 'api_key' in config['API']:
        api_key = input("Entrez votre clé API: ")
        config['API'] = {'api_key': api_key}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        return api_key
    else:
        return config['API']['api_key']

def main():
    api_key = get_api_key()
    source_file = sys.argv[1] if len(sys.argv) > 1 else 'default_1_url.txt'
    fieldnames = ["url", "target", "linkType", "linkRels", "linkText"]
    with open('url_internals.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
    if source_file == 'default_1_url.txt':
        with open('default_1_url.txt', 'w') as fichier:
            fichier.write('https://www.babbar.tech')
    with open(source_file, 'r') as file:
        urls = file.read().splitlines()
        for url in urls:
            url_n = url.replace("://", "_")
            url_n = url_n.replace(".", "_")
            url_n = url_n.replace("/", "_")
            links_data = u_current_internals_from(url, api_key)
            for link in links_data:
                row = {
                    "url": url,
                    "target": link["target"],
                    "linkType": link["linkType"],
                    "linkRels": "|||".join(link["linkRels"]) if link["linkRels"] else "",
                    "linkText": link["linkText"]
                }
                with open('url_internals.csv', 'a', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writerow(row)

if __name__ == "__main__":
    main()