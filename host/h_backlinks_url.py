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
import csv
import pandas as pd
import requests
import json
import sys
import configparser
import os
import time

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

def h_backlinks_u(host, api_token, sort="desc", type="semanticValue"):
    api_url = "https://www.babbar.tech/api/host/backlinks/url"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "host": host,
        "limit": 30000,
        "sort": sort,
        "type": type
    }
    params = {
        "api_token": api_token
    }
    response = requests.post(api_url, headers=headers, params=params, json=payload)
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        time.sleep(60)
    try:
        data = response.json()
        if "links" in data:
            return data["links"]
        else:
            return []
    except json.decoder.JSONDecodeError:
        print("Erreur : Réponse JSON invalide")
        return []

def remove_duplicates_from_csv(file_name):
    df = pd.read_csv(file_name)
    df = df.drop_duplicates()
    df.to_csv(file_name, index=False)

def main():
    api_key = get_api_key()
    hosts_file = sys.argv[1] if len(sys.argv) > 1 else 'default_hosts.txt'
    if hosts_file == 'default_hosts.txt':
        with open('default_hosts.txt', 'w') as fichier:
            fichier.write('www.babbar.tech')
    with open(hosts_file, 'r') as f:
        hosts = [line.strip() for line in f]
        for host in hosts:
            data = h_backlinks_u(host, api_key)
            csv_file = f'{host}_bl.csv'
            if not os.path.exists(csv_file):
                with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['source', 'target', 'linkText', 'linkType', 'linkRels', 'language', 'pageValue', 'semanticValue', 'babbarAuthorityScore', 'pageTrust'])
            with open(csv_file, 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                for row in data:
                    writer.writerow([row.get('source', ''), row.get('target', ''), row.get('linkText', ''), row.get('linkType', ''), row.get('linkRels', []), row.get('language', ''), row.get('pageValue', ''), row.get('semanticValue', ''), row.get('babbarAuthorityScore', ''), row.get('pageTrust', '')])
            remove_duplicates_from_csv(csv_file)

if __name__ == "__main__":
    main()