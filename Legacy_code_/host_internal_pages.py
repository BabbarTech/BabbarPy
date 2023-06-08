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

def get_internal_pages(host, API_KEY):
    a = 0
    list01 = [" "]
    pages = pd.DataFrame()
    url = "https://www.babbar.tech/api/host/pages/internal?api_token="+API_KEY
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    while list01 != []:
        data = '{"host": "'+str(host)+'", "offset": '+str(a)+', "n": 500}'
        resp = requests.post(url, headers=headers, data=data)
        if resp.status_code != 200:
            print("STATUS CODE INVALID")
            print(resp.status_code)
            list01 = []
            break
        else:
            remain = int(resp.headers.get('X-RateLimit-Remaining'))
            if remain == 0:
                time.sleep(60)
            list01 = resp.json()
            pages_fetch = pd.DataFrame(list01, columns = ['url', 'inLinksExternal', 'inLinksInternal', 'pageValue', 'pageTrust', 'semanticValue', 'internalElementValue'])
            pages = pd.concat([pages, pages_fetch])
            a = a +1
    return(pages)

def internal_pages_to_csv(host, API):
    df = get_internal_pages(host, API)
    df.to_csv(f'{host}_internalpages.csv')

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
        for host in hosts:
            internal_pages_to_csv(host,api_key)

if __name__ == "__main__":
    main()
