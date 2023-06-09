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
import pandas as pd
import requests
from requests.structures import CaseInsensitiveDict
import time
import configparser
import sys
import os

def h_fetches(host, lang, API_KEY, data=[""]):
    a = 0
    data_list = []
    url = "https://www.babbar.tech/api/host/fetches/list?api_token=" + API_KEY
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    while True:
        data = {
            "host": host,
            "status": -1,
            "lang": lang,
            "offset": a,
            "n": 499
        }
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code != 200:
            print("STATUS CODE INVALID")
            print(resp.status_code)
            break
        else:
            try:
                aList = resp.json()
                if isinstance(aList, list):
                    if not aList:  
                        print("No more data.")
                        break
                    remain = int(resp.headers.get('X-RateLimit-Remaining'))
                    if remain == 0:
                        time.sleep(60)
                    for entry in aList:
                        updated_entry = {
                            'host': host,
                            'url': entry['url'],
                            'lang': entry['lang'],
                            'http': entry['http']
                        }
                        data_list.append(updated_entry)
                    a += 1
                else:
                    print("Invalid JSON response:", aList)
                    break
            except ValueError:
                print("Invalid JSON response")
                break
    return data_list

def h_fetches_to_csv(hosts_file, lang, API):
    data_list = []
    with open(hosts_file, 'r') as f:
        hosts = [line.strip() for line in f]
        for host in hosts:
            data_list.extend(h_fetches(host, lang, API))
    df = pd.DataFrame(data_list, columns=['host', 'url', 'lang', 'http'])
    df.to_csv('hosts_data.csv', index=False)

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
    h_fetches_to_csv(hosts_file, 'all', api_key)

if __name__ == "__main__":
    main()
