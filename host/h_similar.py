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
import time
import configparser
import os
import sys

def h_similar(api_key, host):
    json_payload = {
        "host": host,
        "n": 100
    }
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {'api_token': api_key}
    url = "https://www.babbar.tech/api/host/similar"
    response = requests.post(url, headers=headers, params=params, json=json_payload)
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        print(f"holding at {host}")
        time.sleep(60)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f'Request failed with status code {response.status_code}')

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
    hosts_file = sys.argv[1] if len(sys.argv) > 1 else 'default_hosts.txt'
    if hosts_file == 'default_hosts.txt':
        with open('default_hosts.txt', 'w') as fichier:
            fichier.write('www.babbar.tech')
    with open(hosts_file, 'r') as f:
        hosts = [line.strip() for line in f]
        with open('host_similar.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, ["host", "similar", "lang", "score"])
            writer.writeheader()
            for host in hosts:
                data = h_similar(api_key, host)
                for row in data:
                    row['host'] = host
                    writer.writerow(row)

if __name__ == "__main__":
    main()