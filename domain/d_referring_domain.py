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

def d_referring_domain(domain, api_key):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    url = 'https://www.babbar.tech/api/domain/backlinks/domain'
    data = {
        'domain': domain,
        'n': 500,
        'offset': 0
    }
    all_data = []
    while True:
        response = requests.post(url, headers=headers, params=params, json=data)
        response_data = response.json()
        if 'backlinks' in response_data and len(response_data['backlinks']) > 0:
            all_data = response_data['backlinks']
            numBacklinksUsed = response_data.get('numBacklinksUsed', 0)
            numBacklinksTotal = response_data.get('numBacklinksTotal', 0)
            remain = int(response.headers.get('X-RateLimit-Remaining', 1))
            if remain == 0:
                print(f"holding at {data['offset']}")
                time.sleep(60)
            data['offset'] += 1
            return {"all_data":all_data, "numBacklinksUsed" : numBacklinksUsed, "numBacklinksTotal" : numBacklinksTotal}
        break

def main():
    api_key = get_api_key()
    domains_file = sys.argv[1] if len(sys.argv) > 1 else 'default_domains.txt'
    if domains_file == 'default_domains.txt':
        with open('default_domains.txt', 'w') as fichier:
            fichier.write('babbar.tech')
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f]
        with open('domain_list_ref_domains_overview.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['domain', 'number of backlinks used', 'Total number of backlinks'])
        for domain in domains:
            dict_data = d_referring_domain(domain, api_key)
            all_data = dict_data['all_data']
            numBacklinksUsed = dict_data['numBacklinksUsed']
            numBacklinksTotal = dict_data['numBacklinksTotal']
            with open(f'{domain}_d_anchors.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['domain', 'anchor text'])
            with open(f'{domain}_d_anchors.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                for row in all_data:
                    anchors = ", ".join([anchor for anchor in row.get('anchors', [])])
                    writer.writerow([row.get('domain', ''), anchors])
            with open('domain_list_ref_domains_overview.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([domain, numBacklinksUsed, numBacklinksTotal])

if __name__ == "__main__":
    main()