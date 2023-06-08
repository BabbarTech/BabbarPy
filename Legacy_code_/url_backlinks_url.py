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

def urls_backlinks_csv(url, api_key, sort="desc"):
    a = 0
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    plop = 'https://www.babbar.tech/api/url/backlinks/url'
    data = {
        'url': url,
        'limit': 30000,
        'sort': sort,
        "type": "pageValue"
    }
    url_c = url.replace('://','_')
    url_c = url_c.replace('.','')
    all_data = []  # to store all the retrieved data
    max_i = 31
    cur_i = 0
    if not os.path.exists(f'{url_c}_bl.csv'):
        with open(f'{url_c}_bl.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['source', 'target', 'linkText', 'linkType', 'linkRels', 'language', 'pageValue', 'semanticValue', 'babbarAuthorityScore', 'pageTrust'])
    while True:
        response = requests.post(plop, headers=headers, params=params, json=data)
        response_data = response.json()
        cur_i += 1
        if cur_i > max_i:
            print('stopping max iterations reached')
            break
        if 'links' in response_data and len(response_data['links']) > 0:
            all_data = response_data['links']
            remain = int(response.headers.get('X-RateLimit-Remaining', 1))
            if remain == 0:
                time.sleep(60)
            with open(f'{url_c}_bl.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                for row in all_data:
                    writer.writerow([row.get('source', ''), row.get('target', ''), row.get('linkText', ''), row.get('linkType', ''), row.get('linkRels', []), row.get('language', ''), row.get('pageValue', ''), row.get('semanticValue', ''), row.get('babbarAuthorityScore', ''), row.get('pageTrust', '')])
                    a = a+1
                if a == 30000:
                    if sort == "desc":
                        urls_backlinks_csv(url, api_key, sort="asc")
                        break
                    elif sort == "asc":
                        print('60k backlinks already')
                        break
                break
        else:
            break  # no more data to retrieve, break out of the loop

def remove_duplicates_from_csv(file_name):
    df = pd.read_csv(file_name)
    df = df.drop_duplicates()
    df.to_csv(file_name, index=False)

def main():
    api_key = get_api_key()
    urls_file = sys.argv[1] if len(sys.argv) > 1 else 'default_urls.txt'  # Get hosts file from CLI or use default
    if urls_file == 'default_urls.txt':
        with open('default_urls.txt', 'w') as fichier:
            fichier.write('https://www.babbar.tech')
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f]
        for url in urls:
            urls_backlinks_csv(url, api_key)
            print("fetch done")
            url_c = url.replace('://','_')
            url_c = url_c.replace('.','')
            remove_duplicates_from_csv(f'{url_c}_bl.csv')

if __name__ == "__main__":
    main()
