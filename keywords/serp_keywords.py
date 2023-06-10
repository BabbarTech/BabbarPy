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
import datetime

initial_date = datetime.date.today()-datetime.timedelta(weeks=2)

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

def serp_keywords(keyword, api_key, lang="fr", country="FR", date=initial_date):
    offset = 0
    n = 100
    min_ = 1
    max_ = 3
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    url = 'https://www.babbar.tech/api/keyword'
    data = {
        'keyword': keyword,
        "lang": lang,
        "country": country,
        "date": date.strftime("%Y-%m-%d"),
        "feature": "ORGANIC",
        "offset": offset,
        "n": n,
        "min": min_,
        "max": max_
    }
    response = requests.post(url, headers=headers, params=params, json=data)
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        time.sleep(60)
    response_data = response.json()
    return response_data

def main():
    api_key = get_api_key()
    fieldnames=['keywords', 'rank', 'position', 'url', 'date', 'title', 'breadcrumb', 'snippet']
    keywords_file = sys.argv[1] if len(sys.argv) > 1 else 'default_keywords.txt'
    if keywords_file == 'default_keywords.txt':
        with open('default_keywords.txt', 'w') as fichier:
            fichier.write('babbar')
    with open(keywords_file, 'r') as f:
        keywords = [line.strip() for line in f]
    with open('resultats.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    for keyword in keywords:
        data = serp_keywords(keyword, api_key)
        with open('resultats.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for item in data['data']['results']:
                feature = item['feature']
                organic = feature['organic']
                snippet = organic['snippet'].replace('\n', ' ')
                writer.writerow({
                    'keywords': keyword,
                    'rank': item['rank'],
                    'position': organic['position'],
                    'url': organic['url'],
                    'date': data['data']['request']['date'],
                    'title': organic['title'],
                    'breadcrumb': organic['breadcrumb'],
                    'snippet': snippet
                })
    
if __name__ == "__main__":
    main()