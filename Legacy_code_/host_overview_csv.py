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

def h_overview(host, api_key):
    endpoint = 'https://www.babbar.tech/api/host/overview/main'
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    params = {'api_token': api_key}
    payload = {"host": host}
    response = requests.post(endpoint, json=payload, headers=headers, params=params)
    remain = int(response.headers.get('X-RateLimit-Remaining'))
    if remain == 0:
        time.sleep(60)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f'Data collection error : {response.status_code}')

def write_to_csv(data, dict_writer, host):
    dict_writer.writerow({
        'host': host,
        'hostValue': data['hostValue'],
        'hostTrust': data['hostTrust'],
        'semanticValue': data['semanticValue'],
        'babbarAuthorityScore': data['babbarAuthorityScore'],
        'knownUrls': data['knownUrls'],
        'backlinks_linkCount': data['backlinks']['linkCount'],
        'backlinks_hostCount': data['backlinks']['hostCount'],
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
    hosts_file = sys.argv[1] if len(sys.argv) > 1 else 'default_hosts.txt'  # Get hosts file from CLI or use default
    if hosts_file == 'default_hosts.txt':
        with open('default_hosts.txt', 'w') as fichier:
            fichier.write('www.babbar.tech')
    with open(hosts_file, 'r') as f:
        hosts = [line.strip() for line in f]
    keys = ['host', 'hostValue', 'hostTrust', 'semanticValue', 'babbarAuthorityScore', 
            'knownUrls', 'backlinks_linkCount', 'backlinks_hostCount', 
            'backlinks_ipCount', 'backlinks_asCount']
    with open('output.csv', 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        for host in hosts:
            data = h_overview(host, api_key)
            write_to_csv(data, dict_writer, host)

if __name__ == "__main__":
    main()