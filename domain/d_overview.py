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
import json
import requests
import sys
import configparser
import os
import time

def d_overview(domain, api_key):
    endpoint = 'https://www.babbar.tech/api/domain/overview/main'
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    params = {'api_token': api_key}
    payload = {"domain": domain}
    response = requests.post(endpoint, json=payload, headers=headers, params=params)
    remain = int(response.headers.get('X-RateLimit-Remaining'))
    if remain == 0:
        time.sleep(60)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f'Data collection error : {response.status_code}')

def write_to_csv(data, dict_writer, domain):
    dict_writer.writerow({
        'domain': domain,
        'domainValue': data['domainValue'],
        'domainTrust': data['domainTrust'],
        'semanticValue': data['semanticValue'],
        'babbarAuthorityScore': data['babbarAuthorityScore'],
        'knownUrls': data['knownUrls'],
        'backlinks_linkCount': data['backlinks']['linkCount'],
        'backlinks_hostCount': data['backlinks']['hostCount'],
        'backlinks_domainCount': data['backlinks']['domainCount'],
        'backlinks_ipCount': data['backlinks']['ipCount'],
        'backlinks_asCount': data['backlinks']['asCount']
    })

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
    domains_file = sys.argv[1] if len(sys.argv) > 1 else 'default_domains.txt'  # Get domains file from CLI or use default
    if domains_file == 'default_domains.txt':
        with open('default_domains.txt', 'w') as fichier:
            fichier.write('babbar.tech')
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f]
    keys = ['domain', 'domainValue', 'domainTrust', 'semanticValue', 'babbarAuthorityScore', 
            'knownUrls', 'backlinks_linkCount', 'backlinks_hostCount', 'backlinks_domainCount', 
            'backlinks_ipCount', 'backlinks_asCount']
    with open('d_output.csv', 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        for domain in domains:
            data = d_overview(domain, api_key)
            write_to_csv(data, dict_writer, domain)

if __name__ == "__main__":
    main()