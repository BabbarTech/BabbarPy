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

def h_spotfinder(api_key, term):
    url = 'https://www.babbar.tech/api/host/spotsfinder'
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    params = {'api_token': api_key}
    data = {'content': term, 'lang': 'fr'}
    response = requests.post(url, headers=headers, params=params, json=data)
    if 'X-RateLimit-Remaining' in response.headers:
        remain = int(response.headers.get('X-RateLimit-Remaining'))
        if remain == 0:
            time.sleep(60)
    if response.status_code !=200:
        print(f'Data collection error : {response.status_code}')
        return []
    else:
        results = response.json()
        rows = []
        for result in results:
            row = [term, result['host'], result['score']]
            urls = result['urls']
            for i in range(3):
                if i < len(urls):
                    row.extend([urls[i]['similar'], urls[i]['score']])
                else:
                    row.extend(['', ''])
            rows.append(row)
        return rows

def main():
    api_key = get_api_key()
    terms_file = sys.argv[1] if len(sys.argv) > 1 else 'default_terms.txt'
    if terms_file == 'default_terms.txt':
        with open('default_terms.txt', 'w') as fichier:
            fichier.write('babbar et yourtext guru les meilleurs outil seo')
    with open(terms_file, 'r') as f:
        terms = [line.strip() for line in f]
        with open('spotfinder_results.csv', 'w', newline='') as foo:
            writer = csv.writer(foo, lineterminator='\n')
            writer.writerow(['query', 'host', 'score', 'urls similar 1', 'score 1', 'urls similar 2', 'score 2', 'urls similar 3', 'score 3'])
            for term in terms:
                rows = h_spotfinder(api_key, term)
                for row in rows:
                    writer.writerow(row)

if __name__ == "__main__":
    main()