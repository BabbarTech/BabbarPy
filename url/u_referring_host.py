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

def u_referring_host(url_b, api_key):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    url = 'https://www.babbar.tech/api/url/backlinks/host'
    data = {
        'url': url_b,
        'n': 499,
        'offset': 0
    }
    all_data = []
    last_data = None
    while True:
        response = requests.post(url, headers=headers, params=params, json=data)
        response_data = response.json()
        numBacklinksUsed = response_data.get('numBacklinksUsed', 0)
        numBacklinksTotal = response_data.get('numBacklinksTotal', 0)
        part_data = response_data.get('backlinks', [])
        # Exit the loop when no more new backlinks are received
        if part_data == last_data:
            break
        last_data = part_data
        remain = int(response.headers.get('X-RateLimit-Remaining', 1))
        if remain == 0:
            print(f"holding at {data['offset']}")
            time.sleep(60)
        data['offset'] += len(part_data)
        all_data.extend(part_data)
    return {"all_data":all_data, "numBacklinksUsed" : numBacklinksUsed, "numBacklinksTotal" : numBacklinksTotal}

def main():
    api_key = get_api_key()
    urls_file = sys.argv[1] if len(sys.argv) > 1 else 'default_urls.txt'
    if urls_file == 'default_urls.txt':
        with open('default_urls.txt', 'w') as fichier:
            fichier.write('https://www.babbar.tech\nhttps://blog.babbar.tech')
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f]
        for url in urls:
            url_c = url.replace("://", "_")
            url_c = url_c.replace("/", "_")
            url_c = url_c.replace(".", "_")
            all_data = u_referring_host(url, api_key)
            with open(f'{url_c}_anchors.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['host', 'anchor text'])
                for row in all_data["all_data"]:
                    anchors = ", ".join([anchor for anchor in row.get('anchors', [])])
                    writer.writerow([row.get('host', ''), anchors])
            # Open file in append mode and only write header if file does not exist.
            file_exists = os.path.isfile('url_list_ref_hosts_overview.csv')
            with open('url_list_ref_hosts_overview.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(['url', 'number of backlinks used', 'Total number of backlinks'])
                writer.writerow([url_c, all_data['numBacklinksUsed'], all_data['numBacklinksTotal']])

if __name__ == "__main__":
    main()