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
import requests
import sys
import configparser
import os
import json
import time
import pandas as pd

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

def u_backlinks_u(url, api_token, sort="desc", type="semanticValue"):
    api_url = "https://www.babbar.tech/api/url/backlinks/url"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
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
    urls_file = sys.argv[1] if len(sys.argv) > 1 else 'default_urls.txt'
    if urls_file == 'default_urls.txt':
        with open('default_urls.txt', 'w') as fichier:
            fichier.write('https://blog.babbar.tech/\nhttps://www.babbar.tech/')
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f]
        for url in urls:
            data = u_backlinks_u(url, api_key)
            url_c = url.replace('://','_')
            url_c = url_c.replace('/','_')
            url_c = url_c.replace('.','')
            csv_file = f'{url_c}_bl.csv'
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