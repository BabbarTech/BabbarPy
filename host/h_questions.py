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

def h_questions(host, api_key):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    url = 'https://www.babbar.tech/api/host/questions'
    data = {
        'host': host
    }
    response = requests.post(url, headers=headers, params=params, json=data)
    response_data = response.json()
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        print(f"holding at {data['offset']}")
        time.sleep(60)
    return response_data

def main():
    api_key = get_api_key()
    fields = ["host", "lang", "question", "score"]
    hosts_file = sys.argv[1] if len(sys.argv) > 1 else 'default_hosts.txt'
    if hosts_file == 'default_hosts.txt':
        with open('default_hosts.txt', 'w') as fichier:
            fichier.write('blog.babbar.tech')
    with open(hosts_file, 'r') as f:
        hosts = [line.strip() for line in f]
        with open('host_questions_list.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
        for host in hosts:
            dict_data = h_questions(host, api_key)
            with open('host_questions_list.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                for item in dict_data:
                    item["host"] = host
                    writer.writerow(item)

if __name__ == "__main__":
    main()